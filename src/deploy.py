#!/usr/bin/env python3
import webbrowser

import data_import
from api_setup import configure_api
from service import service
from settings import get_settings


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


def deploy():
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

    configure_api("self-signed", passwords['api'], passwords["keystore_password"])

    print("Finished deploying Montagu")
    # webbrowser.open("https://localhost:8080/")
    # webbrowser.open("http://localhost:8081/")

if __name__ == "__main__":
    deploy()
