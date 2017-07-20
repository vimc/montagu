#!/usr/bin/env python3
import shutil
import webbrowser
from os import chdir
from os.path import abspath, dirname
from typing import Dict

import data_import
import paths
from ascii_art import print_ascii_art
import backup
from certificates import get_ssl_certificate
from service import service
from service_config import configure_api, configure_proxy
from service_config.api_config import get_token_keypair
from settings import get_settings


def migrate_schema(db_password):
    pass


def generate_passwords() -> Dict[str, str]:
    return {
        "api": "",
        "schema_migrator": ""
    }


def set_passwords_for_db_users(passwords):
    pass


def stop(settings):
    service.stop(settings["port"], persist_volumes=settings["persist_data"])


def _deploy():
    print_ascii_art()
    print("Beginning Montagu deploy")
    status = service.status
    volume_present = service.volume_present
    is_first_time = (status is None) and (not volume_present)
    if is_first_time:
        print("Montagu not detected: Beginning new deployment")
    else:
        print("Montagu status: {}. Data volume present: {}".format(status, volume_present))

    settings = get_settings(is_first_time)

    # If Montagu is running, back it up before tampering with it
    if (status == "running") and settings["backup"]:
        backup.backup(settings)

    # Stop Montagu if it is running (and delete data volume if persist_data is False)
    if not is_first_time:
        stop(settings)

    # Schedule backups
    if settings["backup"]:
        backup.schedule(settings)

    # Start Montagu again
    service.start(settings["port"])
    try:
        configure_montagu(is_first_time, settings)
    except:
        print("An error occurred before deployment could be completed. Stopping Montagu")
        stop(settings)
        raise

    print("Finished deploying Montagu")
    if settings["open_browser"]:
        webbrowser.open("https://localhost:{}/".format(settings["port"]))


def configure_montagu(is_first_time, settings):
    passwords = generate_passwords()
    set_passwords_for_db_users(passwords)

    # Do things to the database
    if (not is_first_time) and settings["persist_data"]:
        print("Skipping data import: 'persist_data' is set, and this is not a first-time deployment")
    else:
        data_import.do(settings)
    # migrate_schema(passwords['schema_migrator'])

    # Push secrets into containers
    cert_paths = get_ssl_certificate(settings["certificate"])
    token_keypair_paths = get_token_keypair()

    configure_api(passwords['api'], token_keypair_paths)
    configure_proxy(cert_paths)


def delete_safely(path):
    try:
        shutil.rmtree(path)
    except:
        pass


def deploy():
    try:
        _deploy()
    finally:
        delete_safely(paths.ssl)
        delete_safely(paths.token_keypair)

if __name__ == "__main__":
    abspath = abspath(__file__)
    chdir(dirname(abspath))
    deploy()
