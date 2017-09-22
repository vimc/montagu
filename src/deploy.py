#!/usr/bin/env python3
import webbrowser
from os import chdir
from os.path import abspath, dirname
from time import sleep

import backup
import data_import
import database
import orderly
import paths
from ascii_art import print_ascii_art
from certificates import get_ssl_certificate
from cli import add_test_user
from git import git_check
from service import service
from service_config import configure_api, configure_proxy
from service_config.api_config import get_token_keypair, configure_reporting_api
from settings import get_settings
from last_deploy import last_deploy_update

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

    # Check that the deployment environment is clean enough
    git_check(settings)

    # If Montagu is running, back it up before tampering with it
    if (status == "running") and settings["backup"]:
        backup.backup(settings)

    # Stop Montagu if it is running (and delete data volume if persist_data is False)
    if not is_first_time:
        service.stop(settings)

    # Schedule backups
    if settings["backup"]:
        backup.schedule(settings)

    # Start Montagu again
    service.start(settings["port"], settings["hostname"])
    try:
        configure_montagu(is_first_time, settings)
    except Exception as e:
        print("An error occurred before deployment could be completed. Stopping Montagu")
        print(e)
        service.stop(settings)
        raise

    if settings["add_test_user"] is True:
        add_test_user()

    last_deploy_update()

    print("Finished deploying Montagu")
    if settings["open_browser"]:
        sleep(1)
        webbrowser.open("https://localhost:{}/".format(settings["port"]))


def configure_montagu(is_first_time, settings):
    # Do things to the database
    if (not is_first_time) and settings["persist_data"]:
        print("Skipping data import: 'persist_data' is set, and this is not a first-time deployment")
    else:
        data_import.do(settings)
        orderly.create_orderly_store(settings)

    passwords = database.setup(settings["use_real_passwords"])

    # Push secrets into containers
    cert_paths = get_ssl_certificate(settings["certificate"])
    token_keypair_paths = get_token_keypair()

    configure_api(passwords['api'], token_keypair_paths, settings["hostname"], settings["use_real_passwords"])
    configure_reporting_api(token_keypair_paths)
    configure_proxy(cert_paths)


def deploy():
    try:
        _deploy()
    finally:
        paths.delete_safely(paths.ssl)
        paths.delete_safely(paths.token_keypair)
        paths.delete_safely(paths.config)
        paths.delete_safely(paths.orderly)

if __name__ == "__main__":
    abspath = abspath(__file__)
    chdir(dirname(abspath))
    deploy()
