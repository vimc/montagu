import random
import string
from subprocess import run

import psycopg2

import versions
from docker_helpers import get_image_name, pull
from service import service, network_name
from service_config import api_db_user
from settings import get_secret

root_user = "vimc"


def user_configs(password_group):
    # Later, read these from a yml file?
    return [
        UserConfig(api_db_user, 'all', VaultPassword(password_group, api_db_user)),
        UserConfig('import', 'all', VaultPassword(password_group, 'import')),
        UserConfig('orderly', 'all', VaultPassword(password_group, 'orderly')),
        UserConfig('readonly', 'readonly', VaultPassword(password_group, 'readonly')),
    ]


class GeneratePassword:
    def get(self):
        return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(50))

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
        return "database/{password_group}/users/{username}".format(
            password_group = self.password_group, username = self.username)

    def __str__(self):
        if self.password_group is None:
            return "Using default password value"
        else:
            return "From vault at " + self._path()


class UserConfig:
    def __init__(self, name, permissions, password_source):
        self.name = name
        self.permissions = permissions  # Currently, this can only be 'all', but the idea is to extend this config later
        self.password_source = password_source
        self._password = None

    # Lazy password resolution
    @property
    def password(self):
        if self._password is None:
            self._password = self.password_source.get()
        return self._password

def set_root_password(password):
    query = "ALTER USER {user} WITH PASSWORD '{password}'".format(user=root_user, password=password)
    service.db.exec_run('psql -U {user} -d postgres -c "{query}"'.format(user=root_user, query=query))


def connect(user, password):
    conn_settings = {
        "host": "localhost",
        "port": 5432,
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
      CREATE ROLE {name} LOGIN PASSWORD '{password}';
   END IF;
END
$body$""".format(name=user.name, password=user.password)
    db.execute(sql)


def set_password(db, user):
    db.execute("ALTER USER {name} WITH PASSWORD '{password}'".format(name=user.name, password=user.password))


def revoke_all(db, user):
    def revoke_all_on(what):
        db.execute("REVOKE ALL PRIVILEGES ON ALL {what} IN SCHEMA public FROM {name}".format(name=user.name, what=what))

    revoke_all_on("tables")
    revoke_all_on("sequences")
    revoke_all_on("functions")


def grant_all(db, user):
    def grant_all_on(what):
        db.execute("GRANT ALL PRIVILEGES ON ALL {what} IN SCHEMA public TO {name}".format(name=user.name, what=what))
    print("  - Granting all permissions to {name}".format(name=user.name))
    grant_all_on("tables")
    grant_all_on("sequences")
    grant_all_on("functions")


def grant_readonly(db, user):
    print("  - Granting readonly permissions to {name}".format(name=user.name))
    db.execute("GRANT SELECT ON ALL TABLES IN SCHEMA public TO {name}".format(name=user.name))


def set_permissions(db, user):
    revoke_all(db, user)
    if user.permissions == 'all':
        grant_all(db, user)
    elif user.permissions == 'readonly':
        grant_readonly(db, user)
    else:
        template = "Unhandled permission type '{permissions}' for user '{name}'"
        raise Exception(template.format(name=user.name, permissions=user.permissions))


def migrate_schema(db_password):
    image = get_image_name("montagu-migrate", versions.db)
    pull(image)
    run([
        "docker", "run",
        "--rm",
        "--network=" + network_name,
        image,
        "migrate", "-user=" + root_user, "-password=" + db_password
    ], check=True)


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


def setup(password_group):
    print("Setting up database users")
    print("- Scrambling root password")
    if password_group is not None:
        root_password = GeneratePassword().get()
        set_root_password(root_password)
    else:
        root_password = 'changeme'

    print("- Getting user configurations")
    users = user_configs(password_group)

    print("- Getting user passwords")
    passwords = {}
    for user in users:
        print(" - {name}: {source}".format(name=user.name, source=user.password_source))
        passwords[user.name] = user.password

    print("- Updating database users")
    for_each_user(root_password, users, setup_user)

    print("- Migrating database schema")
    migrate_schema(root_password)

    print("- Refreshing permissions")
    # The migrations may have added new tables, so we should set the permissions
    # again, in case users need to have permissions on these new tables
    for_each_user(root_password, users, set_permissions)

    return passwords
