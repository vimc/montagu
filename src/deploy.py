#!/usr/bin/env python3
import webbrowser

import shutil

import data_import
import paths
from api_setup import configure_api
from certificates import get_keystore
from service import service
from settings import get_settings
from webapp_config import configure_webapps


def backup():
    pass


def setup_new_data_volume():
    pass


def migrate_schema(db_password):
    pass


def generate_passwords():
    return {
        "api": None,
        "schema_migrator": None,
        "keystore_password": "password"
    }


def set_passwords_for_db_users(passwords):
    pass


def _deploy():
    print("Beginning Montagu deploy")
    status = service.status
    is_first_time = status is None
    if is_first_time:
        print("Montagu not detected: Beginning new deployment")
    else:
        print("Montagu status: {}".format(status))

    settings = get_settings(is_first_time)
    if not is_first_time:
        service.stop()
        backup()

    if settings["persist_data"] and is_first_time:
        setup_new_data_volume()

    service.start()
    passwords = generate_passwords()
    set_passwords_for_db_users(passwords)

    migrate_schema(passwords['schema_migrator'])
    if not is_first_time and settings["persist_data"]:
        print("Skipping data import: 'persist_data' is set, and this is not a first-time deployment")
    else:
        data_import.do(settings)

    keystore_password = passwords["keystore_password"]
    keystore_path = get_keystore("self-signed", keystore_password)
    configure_api(passwords['api'], keystore_path, keystore_password)
    configure_webapps(keystore_password)

    print("Finished deploying Montagu")
    if settings["open_browser"]:
        webbrowser.open("https://localhost:8080/")
        webbrowser.open("https://localhost:8081/")
        webbrowser.open("https://localhost:8082/")


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
