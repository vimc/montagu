import random
import string
from subprocess import run
from types import SimpleNamespace

import psycopg2

import versions
from docker_helpers import get_image_name, pull, exec_safely
from service_config import api_db_user
from settings import get_secret

root_user = "vimc"
# these tables should only be modified via sql migrations
protected_tables = ["gavi_support_level", "activity_type",
                    "burden_outcome",
                    "gender",
                    "responsibility_set_status",
                    "impact_outcome",
                    "gavi_support_level",
                    "support_type",
                    "touchstone_status",
                    "permission",
                    "role",
                    "role_permission"]


def user_configs(password_group):
    # Later, read these from a yml file?
    return [
        UserConfig(api_db_user, 'all',
                   VaultPassword(password_group, api_db_user)),
        UserConfig('import', 'all', VaultPassword(password_group, 'import')),
        UserConfig('orderly', 'all', VaultPassword(password_group, 'orderly')),
        UserConfig('readonly', 'readonly',
                   VaultPassword(password_group, 'readonly')),
    ]


class GeneratePassword:
    def get(self):
        return ''.join(random.SystemRandom().choice(
            string.ascii_uppercase + string.digits) for _ in range(50))

    def __str__(self):
        return "Generated"


class VaultPassword:
    def __init__(self, password_group, username):
        self.password_group = password_group
        self.username = username

    def get(self):
        if self.password_group is None:
            return "changeme" if self.username == "vimc" else self.username
        else:
            return get_secret(self._path(), field="password")

    def _path(self):
        if self.password_group is None:
            raise Exception("_path() is not defined without a password group")
        else:
            return "database/{password_group}/users/{username}".format(
                password_group=self.password_group, username=self.username)

    def __str__(self):
        if self.password_group is None:
            return "Using default password value"
        else:
            return "From vault at " + self._path()


class UserConfig:
    def __init__(self, name, permissions, password_source, option=None):
        self.name = name
        self.permissions = permissions  # Currently, this can only be 'all', but the idea is to extend this config later
        self.password_source = password_source
        self.option = option.upper() if option else ""
        self._password = None

    # Lazy password resolution
    @property
    def password(self):
        if self._password is None:
            self._password = self.password_source.get()
        return self._password

    @classmethod
    def create(self, name, permissions, password_group, option):
        password = VaultPassword(password_group, name)
        return UserConfig(name, permissions, password, option)


def set_root_password(service, password):
    query = "ALTER USER {user} WITH PASSWORD '{password}'".format(
        user=root_user, password=password)
    service.db.exec_run(
        'psql -U {user} -d postgres -c "{query}"'.format(user=root_user,
                                                         query=query))


def connect(user, password, host="localhost", port=5432):
    conn_settings = {
        "host": host,
        "port": port,
        "name": "montagu",
        "user": user,
        "password": password
    }
    conn_string_template = "host='{host}' port='{port}' dbname='{name}' user='{user}' password='{password}'"
    conn_string = conn_string_template.format(**conn_settings)
    return psycopg2.connect(conn_string)


def create_user(db, user):
    sql = """DO
$body$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = '{name}') THEN
      CREATE ROLE {name} {option} LOGIN PASSWORD '{password}';
   END IF;
END
$body$""".format(name=user.name, password=user.password, option=user.option)
    db.execute(sql)


def set_password(db, user):
    db.execute(
        "ALTER USER {name} WITH PASSWORD '{password}'".format(name=user.name,
                                                              password=user.password))


def revoke_all(db, user):
    def revoke_all_on(what):
        db.execute(
            "REVOKE ALL PRIVILEGES ON ALL {what} IN SCHEMA public FROM {name}".format(
                name=user.name, what=what))

    revoke_all_on("tables")
    revoke_all_on("sequences")
    revoke_all_on("functions")


def revoke_write_on_protected_tables(db, user):
    def revoke_specific_on(what):
        db.execute(
            "REVOKE INSERT, UPDATE, DELETE ON {what} FROM {name}".format(
                name=user.name, what=what))

    for table in protected_tables:
        revoke_specific_on(table)


def grant_all(db, user):
    def grant_all_on(what):
        db.execute(
            "GRANT ALL PRIVILEGES ON ALL {what} IN SCHEMA public TO {name}".format(
                name=user.name, what=what))

    print("  - Granting all permissions to {name}".format(name=user.name))
    grant_all_on("tables")
    grant_all_on("sequences")
    grant_all_on("functions")


def grant_readonly(db, user):
    print("  - Granting readonly permissions to {name}".format(name=user.name))
    db.execute("GRANT SELECT ON ALL TABLES IN SCHEMA public TO {name}".format(
        name=user.name))


def set_permissions(db, user):
    revoke_all(db, user)
    if user.permissions == 'all':
        grant_all(db, user)
    elif user.permissions == 'readonly':
        grant_readonly(db, user)
    elif user.permissions == 'pass':
        pass
    else:
        template = "Unhandled permission type '{permissions}' for user '{name}'"
        raise Exception(
            template.format(name=user.name, permissions=user.permissions))


def migrate_schema_core(service, root_password):
    network_name = service.network_name
    print("- migrating schema")
    image = "vimc/{name}:{version}".format(name="montagu-migrate",
                                           version=versions.db)
    pull(image)
    cmd = ["docker", "run", "--rm", "--network=" + network_name, image] + \
          ["-user=vimc", "-password=" + root_password, "migrate"]
    run(cmd, check=True)


def setup_user(db, user):
    print(" - " + user.name)
    create_user(db, user)
    set_password(db, user)
    set_permissions(db, user)


def for_each_user(root_password, users, operation):
    """Operation is a callback (function) that takes the connection cursor
    and a UserConfig object"""
    with connect(root_user, root_password) as conn:
        with conn.cursor() as cur:
            for user in users:
                operation(cur, user)
        conn.commit()


def setup(service):
    print("Waiting for the database to accept connections")
    exec_safely(service.db, ["montagu-wait.sh", "3600"], check=True)
    password_group = service.settings["password_group"]
    print("Setting up database users")
    print("- Scrambling root password")
    if password_group is not None:
        root_password = GeneratePassword().get()
    else:
        root_password = 'changeme'
    set_root_password(service, root_password)

    print("- Getting user configurations")
    users = user_configs(password_group)

    print("- Getting user passwords")
    passwords = {}
    for user in users:
        print(" - {name}: {source}".format(name=user.name,
                                           source=user.password_source))
        passwords[user.name] = user.password

    # NOTE: As I work through this - why not set up users *after* the
    # schema migration?  This is because the migration user needs to
    # exist, though in practice we don't use them so this could be
    # reordered later.
    print("- Updating database users")
    for_each_user(root_password, users, setup_user)

    print("- Migrating database schema")
    migrate_schema_core(service, root_password)

    print("- Refreshing permissions")
    # The migrations may have added new tables, so we should set the permissions
    # again, in case users need to have permissions on these new tables
    for_each_user(root_password, users, set_permissions)

    # Revoke specific permissions now that all tables have been created.
    for_each_user(root_password, users, revoke_write_on_protected_tables)

    setup_streaming_replication(root_password, service)

    return passwords


# NOTE: it might be worth revisiting this to not run this script
# directly (that requires corresponding changes in montagu-db to move
# the inline sql into a standalone .sql file and then getting psql to
# run it via docker exec - it must run as the vimc user).  The
# passwords might move directly under control here using set_password
# (but these are special users so we'd not want to use the rest of the
# user machinery).  But I suggest waiting until the restore is done
# VIMC-1560) because that is likely to affect how we deal with users
def setup_streaming_replication(root_password, service):
    if service.settings['enable_db_replication']:
        print("Setting up streaming replication")
        password_group = service.settings['password_group']
        barman = UserConfig.create("barman", "pass",
                                   password_group, "superuser")
        streaming_barman = UserConfig.create("streaming_barman", "pass",
                                             password_group, "replication")
        with connect(root_user, root_password) as conn:
            with conn.cursor() as db:
                create_user(db, barman)
                create_user(db, streaming_barman)

        pw_barman = VaultPassword(password_group, "barman").get()
        pw_stream = VaultPassword(password_group, "streaming_barman").get()
        cmd = ["enable-replication.sh", pw_barman, pw_stream]
        exec_safely(service.db, cmd, check=True)


def prepare_db_for_import(service):
    print("Preparing databse for import")
    ## NOTE: this could otherwise be done by connecting using the
    ## connection function, but that that requires further changes to
    ## the connect function to allow connection to the postgres
    ## maintenance database.  This way works for now.  This also
    ## allows us to avoid working out what the root password will be
    ## because we're interating without passwords over exec.
    db = service.db
    print("- deleting and recreating database")
    db.exec_run(["dropdb", "-U", "vimc", "--if-exists", "montagu"])
    db.exec_run(["createdb", "-U", "vimc", "montagu"])
    print("- configuring users")
    users = user_configs(service.settings["password_group"])
    for user in users:
        db.exec_run(["createuser", "-U", "vimc", user.name])
