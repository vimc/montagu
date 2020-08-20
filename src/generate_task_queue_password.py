#!/usr/bin/env python3

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
    else:
        print("Overwriting old password for instance: {}".format(instance))
    set_secret(instance_path, random_password(80), password_key)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Please provide a single arg (instance name)")
        exit(1)
    generate_password(sys.argv[1])
