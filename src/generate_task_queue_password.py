#!/usr/bin/env python3

"""
Generate task queue password

Generates a password for the montagu task queue user for a given instance name
(e.g. uat, science, production) and saves it to the vault.

Usage:
  generate_task_queue_password.py <instance name>
"""

import sys
from generate_passwords import random_password
from settings import set_secret, get_secret, list_secrets

secret_root = "task-queue-user/"
password_key = "password"


def generate_password(instance):
    instance_path = "{}{}".format(secret_root, instance)

    exists = (secret_root in list_secrets("")) and \
             (instance in list_secrets(secret_root))
    if not exists:
        print("Creating password for instance: {}".format(instance))
        set_secret(instance_path, random_password(80), password_key)
    else:
        print("Password already exists for instance: {}".format(instance))
        exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Please provide a single arg (instance name)")
        exit(1)
    generate_password(sys.argv[1])
