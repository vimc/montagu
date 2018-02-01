#!/usr/bin/env python3

"""
Generate montagu database passwords

Usage:
  generate_passwords.py add_user <name>
  generate_passwords.py regenerate_passwords <group>
  generate_passwords.py create_password_group [--base=BASE] <name>
"""

import random
import string

from docopt import docopt

from settings import set_secret, list_secrets


def main():
    pass


def random_password(n):
    pool = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join(random.SystemRandom().choice(pool) for _ in range(n))


def list_password_groups():
    return [g[:-1] for g in list_secrets("database")
            if g[-1] == '/' and g != 'users/']


def list_password_group_users(group):
    return list_secrets("database/{group}/users".format(group=group))


def regenerate_passwords(n=80):
    for g in list_password_groups():
        regenerate_passwords_group(g, n)


def regenerate_passwords_group(group, n=80):
    if group not in list_password_groups():
        raise Exception("Password group '{}' does not exist".format(group))
    users = list_password_group_users(group)
    generate_passwords(group, users, n)


def create_password_group(name, base="science", n=80):
    existing = list_password_groups()
    if name in existing:
        raise Exception("Password group '{}' already exists".format(name))
    if base not in existing:
        raise Exception("Password group '{}' does not exist".format(name))
    print("Creating new password group {}".format(name))
    users = list_password_group_users(base)
    generate_passwords(name, users, n)


def add_user(name, n=80):
    groups = list_password_groups()
    print("Generating passwords for user '{}'".format(name))
    for g in groups:
        generate_password(g, name, n)


def generate_passwords(group, users, n):
    print("Generating passwords for group '{}'".format(group))
    for u in users:
        generate_password(group, u, n)


def generate_password(group, user, n):
    p = 'database/{group}/users/{user}'.format(group=group, user=user)
    print("\t - {}".format(p))
    set_secret(p, random_password(n), "password")


def main():
    args = docopt(__doc__)
    if args['add_user']:
        add_user(args['<name>'])
    elif args['create_password_group']:
        base = args['--base'] or 'science'
        create_password_group(args['<name>'], base)
    elif args['regenerate_passwords']:
        regenerate_passwords_group(args['<group>'])


if __name__ == "__main__":
    main()
