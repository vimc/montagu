import json
import os
from getpass import getpass
from os.path import abspath
from subprocess import check_output, run

from setting_definitions import definitions, vault_required

default_path = 'montagu-deploy.json'


def load_settings(path=default_path):
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

    # now re-write file to make sure only the settings used are persisted
    save_settings(settings)
    return settings


def prepare_for_vault_access(address, quiet=False):
    os.environ["VAULT_ADDR"] = address
    if "VAULT_AUTH_GITHUB_TOKEN" in os.environ:
        if not quiet:
            print("Already authenticated with Vault")
    else:
        token = getpass("Please enter your Vault GitHub personal access token: ")
        os.environ["VAULT_AUTH_GITHUB_TOKEN"] = token
        run(["vault", "login", "-method=github"], check=True)


def validate_settings(path=default_path):
    settings = load_settings(path)
    missing = list(d for d in definitions if d.name not in settings)
    ret = []
    for d in missing:
        if d.is_required(settings):
            ret.append(d.name)
    return ret


def validate_settings_directory(montagu_root):
    files = os.listdir("{}/settings".format(montagu_root))
    files.sort()

    errs = []
    for f in files:
        p = "{}/settings/{}".format(montagu_root, f)
        errs += ["  - settings/{}: {}".format(f, x)
                 for x in validate_settings(p)]
    if errs:
        msg = "Missing configuration entries:\n" + "\n".join(errs)
        raise Exception(msg)


def get_settings(quiet=False, path=default_path):
    settings = load_settings(path)
    missing = list(d for d in definitions if d.name not in settings)

    showed_prompt = False
    if any(missing):
        for d in missing:
            if d.is_required(settings):
                if not showed_prompt:
                    showed_prompt = True
                    print("I'm going to ask you some questions to determine how Montagu should be deployed.\n"
                          "Your answers will be stored in {}.".format(abspath(path)))

                key = d.name
                value = d.ask()
                settings[key] = value

    save_settings(settings)
    if not quiet:
        print("Using these settings from {}:".format(abspath(path)))
        for k, v in settings.items():
            print("- {}: {}".format(k, v))

    # This is a special value within the enum group, but it would be
    # nicer to refer to it as None
    if settings['password_group'] == 'fake':
        settings['password_group'] = None

    if vault_required(settings):
        prepare_for_vault_access(settings["vault_address"], quiet=quiet)

    return settings


def save_settings(settings, path=default_path):
    with open(path, 'w') as f:
        json.dump(settings, f, indent="  ", sort_keys=True)


def get_secret(secret_path, field="value"):
    secret_path = "secret/{}".format(secret_path)
    return check_output(["vault", "read", "-field=" + field, secret_path]).decode('utf-8')


def set_secret(secret_path, value, field="value"):
    secret_path = "secret/{}".format(secret_path)
    pair = "{field}={value}".format(field = field, value = value)
    check_output(["vault", "write", secret_path, pair])


def list_secrets(secret_path):
    secret_path = "secret/{}".format(secret_path)
    x = check_output(["vault", "list", "-format=json", secret_path])
    return json.loads(x.decode("utf-8"))


def save_secret_to_file(secret_path, output, field="value"):
    secret = get_secret(secret_path, field)
    with open(output, 'w') as f:
        f.write(secret)
