import json
import os
from getpass import getpass
from os.path import abspath
from subprocess import check_output

from setting_definitions import definitions, vault_required

path = 'montagu-deploy.json'


def load_settings():
    settings = {}

    try:
        with open(path, 'r') as f:
            data = json.load(f) or {}
    except FileNotFoundError:
        data = {}

    for d in definitions:
        key = d.name
        if key in data:
            settings[key] = data[key]

    return settings


def prepare_for_vault_access(address):
    os.environ["VAULT_ADDR"] = address
    if "VAULT_AUTH_GITHUB_TOKEN" in os.environ:
        print("Already authenticated with Vault")
    else:
        token = getpass("Please enter your Vault GitHub personal access token: ")
        os.environ["VAULT_AUTH_GITHUB_TOKEN"] = token


def get_settings(do_first_time_setup: bool):
    settings = load_settings()
    missing = list(d for d in definitions if d.name not in settings)
    if not do_first_time_setup:
        missing = list(d for d in missing if not d.first_time_only)

    if any(missing):
        print("I'm going to ask you some questions to determine how Montagu should be deployed.\n"
              "Your answers will be stored in {}.".format(abspath(path)))

        for d in missing:
            if d.is_required(settings):
                key = d.name
                value = d.ask()
                settings[key] = value

    save_settings(settings)
    print("Using these settings from {}:".format(abspath(path)))
    for k, v in settings.items():
        print("- {}: {}".format(k, v))

    if vault_required(settings):
        prepare_for_vault_access(settings["vault_address"])

    return settings


def save_settings(settings):
    with open(path, 'w') as f:
        json.dump(settings, f, indent=4)


def get_secret(secret_path, field="value"):
    secret_path = "secret/{}".format(secret_path)
    return check_output(["vault", "read", "-field=" + field, secret_path]).decode('utf-8')


def save_secret(secret_path, output, field="value"):
    secret = get_secret(secret_path, field)
    with open(output, 'w') as f:
        f.write(secret)
