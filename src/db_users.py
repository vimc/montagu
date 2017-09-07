import random
import string

import psycopg2

from service import service
from service_config import api_db_user
from settings import get_secret

root_user = "vimc"


def user_configs():
    # Later, read these from a yml file?
    return [
        UserConfig(api_db_user, 'all', VaultPassword(api_db_user)),
        UserConfig('import', 'all', VaultPassword('import')),
        UserConfig('orderly', 'all', VaultPassword('orderly')),
        UserConfig('readonly', 'readonly', VaultPassword('readonly')),
        UserConfig('schema_migrator', 'all', VaultPassword('schema_migrator')),
    ]


class GeneratePassword:
    def get(self):
        return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(50))

    def __str__(self):
        return "Generated"


class VaultPassword:
    def __init__(self, username):
        self.username = username

    def get(self):
        return get_secret(self.path, field="password")

    @property
    def path(self):
        return "database/users/" + self.username

    def __str__(self):
        return "From vault at " + self.path


class UserConfig:
    def __init__(self, name, permissions, password_source):
        self.name = name
        self.permissions = permissions  # Currently, this can only be 'all', but the idea is to extend this config later
        self.password_source = password_source
        self.password = None

    def get_password(self):
        self.password = self.password_source.get()


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


def setup_user(db, user):
    print(" - " + user.name)
    create_user(db, user)
    set_password(db, user)
    set_permissions(db, user)


def setup(use_real_passwords):
    print("Setting up database users")
    print("- Scrambling root password")
    if use_real_passwords:
        root_password = GeneratePassword().get()
        set_root_password(root_password)
    else:
        root_password = 'changeme'

    print("- Getting user configurations")
    users = user_configs()

    print("- Getting user passwords")
    passwords = {}
    for user in users:
        print(" - {name}: {source}".format(name=user.name, source=user.password_source))
        if use_real_passwords:
            user.get_password()
        else:
            user.password = user.name
        passwords[user.name] = user.password

    print("- Updating database users")
    with connect(root_user, root_password) as conn:
        with conn.cursor() as cur:
            for user in users:
                setup_user(cur, user)
        conn.commit()

    return passwords
