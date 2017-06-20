#!/usr/bin/env python3
import shutil
import webbrowser
from typing import Dict

import data_import
import paths
from ascii_art import print_ascii_art
from certificates import get_ssl_certificate
from service import service
from service_config import configure_api, configure_proxy
from settings import get_settings


def backup():
    pass


def setup_new_data_volume():
    pass


def migrate_schema(db_password):
    pass


def generate_passwords() -> Dict[str, str]:
    return {
        "api": "",
        "schema_migrator": ""
    }


def set_passwords_for_db_users(passwords):
    pass


def _deploy():
    print_ascii_art()
    print("Beginning Montagu deploy")
    status = service.status
    is_first_time = status is None
    if is_first_time:
        print("Montagu not detected: Beginning new deployment")
    else:
        print("Montagu status: {}".format(status))

    settings = get_settings(is_first_time)
    if not is_first_time:
        service.stop(settings["port"])
        backup()

    if settings["persist_data"] and is_first_time:
        setup_new_data_volume()

    service.start(settings["port"])
    passwords = generate_passwords()
    set_passwords_for_db_users(passwords)

    migrate_schema(passwords['schema_migrator'])
    if not is_first_time and settings["persist_data"] is True:
        print("Skipping data import: 'persist_data' is set, and this is not a first-time deployment")
    else:
        data_import.do(settings)

    configure_api(passwords['api'])
    cert_paths = get_ssl_certificate("self-signed")
    configure_proxy(cert_paths)

    print("Finished deploying Montagu")
    if settings["open_browser"]:
        webbrowser.open("https://localhost:{}/".format(settings["port"]))


def delete_safely(path):
    try:
        shutil.rmtree(path)
    except:
        pass


def deploy():
    try:
        _deploy()
    finally:
        delete_safely(paths.artifacts)
        delete_safely(paths.ssl)

if __name__ == "__main__":
    deploy()
