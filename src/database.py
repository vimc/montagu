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

def connect_annex(annex_settings):
    return connect(annex_settings["root_user"],
                   annex_settings["root_password"],
                   annex_settings["host_from_deploy"],
                   annex_settings["port_from_deploy"])

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

def grant_readonly_annex(db, user, annex_settings):
    print(" - annex: mapping {} -> readonly".format(user.name))
    sql1 = "DROP USER MAPPING IF EXISTS FOR {name} " \
           "SERVER montagu_db_annex;".format(name = user.name)
    sql2 = "CREATE USER MAPPING FOR {name} " \
           "SERVER {annex_server_name} " \
           "OPTIONS (user '{annex_readonly_user}', " \
           "password '{annex_readonly_password}');".format(
               name = user.name,
               annex_server_name = annex_settings['server_name'],
               annex_readonly_user = annex_settings['readonly_user'],
               annex_readonly_password = annex_settings['readonly_password'])
    db.execute(sql1)
    db.execute(sql2)

def set_permissions(db, user):
    revoke_all(db, user)
    if user.permissions == 'all':
        grant_all(db, user)
    elif user.permissions == 'readonly':
        grant_readonly(db, user)
    else:
        template = "Unhandled permission type '{permissions}' for user '{name}'"
        raise Exception(template.format(name=user.name, permissions=user.permissions))

def migrate_schema_core(root_password, annex_settings):
    print("- migrating schema")
    image = get_image_name("montagu-migrate", versions.db)
    pull(image)
    placeholders = {
        'montagu_db_annex_host': annex_settings['host'],
        'montagu_db_annex_port': annex_settings['port'],
        'montagu_db_annex_password': annex_settings['readonly_password']}
    cmd = ["docker", "run", "--rm", "--network=" + network_name, image] + \
          ['-placeholders.{}={}'.format(*x) for x in placeholders.items()] + \
          ["-user=vimc", "-password=" + root_password, "migrate"]
    run(cmd, check=True)

def migrate_schema_annex(annex_settings):
    print("- migrating annex schema")
    image = get_image_name("montagu-migrate", versions.db)
    pull(image)
    root_password = annex_settings['root_password']
    host = '{}:{}'.format(annex_settings['host'], annex_settings['port'])
    config_file = "conf/flyway-annex.conf"
    cmd = ["docker", "run", "--rm", "--network=" + network_name, image,
           "-url=jdbc:postgresql://{}/montagu".format(host),
           "-configFile=" + config_file,
           "-user=vimc", "-password=" + root_password, "migrate"]
    run(cmd, check=True)

def get_annex_settings(settings):
    # This is not the name of the host, but the name used in the postgres
    # scripts to refer to the server (via CREATE SERVER...)
    server_name = "montagu_db_annex"
    # Root and readonly user *on the annex*
    root_user = "vimc"
    readonly_user = "readonly"

    # Below here varies based on fake/real; the only difference within
    # the real types (real/staging) is if we perform migrations.
    if settings["db_annex_type"] == "fake":
        host = "db_annex" # docker container name in compose
        port = 5432
        host_from_deploy = "localhost" # from host
        port_from_deploy = 15432
        readonly_password = "changeme2"
        root_password = "changeme"
        migrate = True
    else:
        host = "annex.montagu.dide.ic.ac.uk" # address of our real server
        port = 15432
        host_from_deploy = host
        port_from_deploy = port
        readonly_password = get_secret("annex/users/readonly", "password")
        root_password = get_secret("annex/users/root", "password")
        migrate = settings["db_annex_type"] == "real"
    return {"host": host,
            "port": port,
            "host_from_deploy": host_from_deploy,
            "port_from_deploy": port_from_deploy,
            "root_user": root_user,
            "root_password": root_password,
            "readonly_user": readonly_user,
            "readonly_password": readonly_password,
            "server_name": server_name,
            "migrate": migrate}

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


def setup(settings):
    annex_settings = setup_annex(settings)

    password_group = settings["password_group"]
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

    # NOTE: As I work through this - why not set up users *after* the
    # schema migration?  This is because the migration user needs to
    # exist, though in practice we don't use them so this could be
    # reordered later.
    print("- Updating database users")
    for_each_user(root_password, users, setup_user)

    print("- Migrating database schema")
    migrate_schema_core(root_password, annex_settings)

    print("- Refreshing permissions")
    # The migrations may have added new tables, so we should set the permissions
    # again, in case users need to have permissions on these new tables
    for_each_user(root_password, users, set_permissions)

    for_each_user(root_password, users, lambda d, u :
                  grant_readonly_annex(d, u, annex_settings))

    return passwords

def setup_annex(settings):
    print("Setting up annex")
    annex_settings = get_annex_settings(settings)
    if annex_settings['migrate']:
        # NOTE: we do this only on production.  This will mean that
        # there are some things that it is hard to test in staging.
        migrate_schema_annex(annex_settings)
        if settings['password_group'] is not None:
            set_password_annex(annex_settings)
    return annex_settings

def set_password_annex(annex_settings):
    print("Setting annex readonly password")
    sql = "ALTER USER readonly WITH PASSWORD '{}'".format(
        annex_settings['readonly_password'])
    with connect_annex(annex_settings) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
