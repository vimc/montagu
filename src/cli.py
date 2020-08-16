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
    settings = get_settings(quiet=True)

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


def add_test_users():
    settings = get_settings(quiet=True)
    service = MontaguService(settings)
    network = service.network_name

    command = [
        "docker", "run",
        #"-it",
        "--network", network
    ]

    password_group = settings['password_group']
    if password_group is not None:
        command += add_secure_config(password_group)

    name = get_image_name("montagu-cli", versions.api)

    print("Attempting to add test user")
    print("Network: " + network)
    run_cmd(command, name, ["add", "Test Admin", "test.admin", "test.admin@imperial.ac.uk", "password", "--if-not-exists"])
    run_cmd(command, name, ["addRole", "test.admin", "user"])
    #run_cmd(command, name, ["addRole", "test.admin", "reports-reviewer"])
    run_cmd(command, name, ["addRole", "test.admin", "touchstone-reviewer"])
    run_cmd(command, name, ["addRole", "test.admin", "admin"])

    run_cmd(command, name, ["add", "Test Modeller", "test.modeller", "test.modeller@imperial.ac.uk", "password", "--if-not-exists"])
    run_cmd(command, name, ["addRole", "test.modeller", "user"])
    #run_cmd(command, name, ["addRole", "test.modeller", "reports-reader"])
    run_cmd(command, name, ["addUserToGroup", "test.modeller", "IC-Garske"])
    run_cmd(command, name, ["addUserToGroup", "test.modeller", "Harvard-Sweet"])


def run_cmd(command, name, args):
    run(command + [name] + args, check=True)


if __name__ == "__main__":
    try:
        absolute_path = abspath(__file__)
        chdir(dirname(absolute_path))
        cli()
    finally:
        paths.delete_safely(paths.config)
