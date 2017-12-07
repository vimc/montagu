#!/usr/bin/env python3
import sys
from os import chdir, makedirs

from subprocess import run
from os.path import abspath, dirname, join

import paths
import versions
from database import user_configs
from docker_helpers import get_image_name
from settings import get_settings
from service import MontaguService

from service_config import api_db_user


def add_secure_config(password_group):
    makedirs(paths.config, exist_ok=True)
    path = join(paths.config, "cli.config.properties")
    user = next(u for u in user_configs(password_group) if u.name == api_db_user)

    print("(Connecting to database as db user '{}')".format(user.name))
    with open(path, 'w') as f:
        print("db.username=" + user.name, file=f)
        print("db.password=" + user.password, file=f)
    return ["-v", abspath(path) + ":/etc/montagu/api/config.properties"]


def cli():
    settings = get_settings(do_first_time_setup=False, quiet=True)

    command = [
        "docker", "run",
        "-it",
        "--network", "montagu_default"
    ]
    password_group = settings['password_group']
    if password_group is not None:
        command += add_secure_config(password_group)

    name = get_image_name("montagu-cli", versions.api)
    args = sys.argv[1:]

    run(command + [name] + args)


def add_test_user():
    settings = get_settings(do_first_time_setup=False, quiet=True)
    service = MontaguService(settings)
    network = service.network_name

    command = [
        "docker", "run",
        "-it",
        "--network", network
    ]

    password_group = settings['password_group']
    if password_group is not None:
        command += add_secure_config(password_group)

    name = get_image_name("montagu-cli", versions.api)
    args = ["add", "Test User", "test.user", "test.user@imperial.ac.uk", "password"]
    run(command + [name] + args)

    args = ["addRole", "test.user", "user"]

    run(command + [name] + args)

    args = ["addRole", "test.user", "reports-reviewer"]

    run(command + [name] + args)

    args = ["addUserToGroup", "test.user", "ALL"]

    run(command + [name] + args)


if __name__ == "__main__":
    try:
        absolute_path = abspath(__file__)
        chdir(dirname(absolute_path))
        cli()
    finally:
        paths.delete_safely(paths.config)
