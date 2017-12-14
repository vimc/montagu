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
from service_config import configure_api, configure_proxy, configure_contrib_portal
from service_config.api_config import get_token_keypair, configure_reporting_api
from settings import get_settings
from last_deploy import last_deploy_update
from notify import Notifier


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
    notifier = Notifier(settings['notify_channel'])

    # Check that the deployment environment is clean enough
    version = git_check(settings)

    deploy_str = "montagu {} (`{}`) on `{}`".format(
        version['tag'] or "(untagged)", version['sha'][:7],
        settings['instance_name'])

    notifier.post("*Starting* deploy of " + deploy_str)

    # If Montagu is running, back it up before tampering with it
    if (status == "running") and settings["backup"]:
        backup.backup(settings)

    # Stop Montagu if it is running (and delete data volume if persist_data is False)
    if not is_first_time:
        notifier.post("*Stopping* previous montagu on `{}` :hand:".format(
            settings['instance_name']))
        service.stop(settings)

    # Schedule backups
    if settings["backup"]:
        backup.schedule(settings)

    # Start Montagu again
    service.start(settings)
    try:
        configure_montagu(is_first_time, settings)
    except Exception as e:
        print("An error occurred before deployment could be completed. Stopping Montagu")
        print(e)
        service.stop(settings)
        try:
            notifier.post("*Failed* deploy of " + deploy_str + " :bomb:")
        except:
            pass
        raise

    if settings["add_test_user"] is True:
        add_test_user()

    last_deploy_update(version)
    notifier.post("*Completed* deploy of " + deploy_str + " :shipit:")

    print("Finished deploying Montagu")
    if settings["open_browser"]:
        sleep(1)
        webbrowser.open("https://localhost:{}/".format(settings["port"]))


def configure_montagu(is_first_time, settings):
    # Do things to the database
    data_exists = (not is_first_time) and settings["persist_data"]
    if data_exists:
        print("Skipping data import: 'persist_data' is set, and this is not a first-time deployment")
    else:
        data_import.do(settings)
    orderly.configure_orderly(not data_exists, settings)

    passwords = database.setup(settings)

    # Push secrets into containers
    cert_paths = get_ssl_certificate(settings["certificate"])
    token_keypair_paths = get_token_keypair()

    send_emails = settings["password_group"] == 'production'
    configure_api(passwords['api'], token_keypair_paths, settings["hostname"], send_emails)
    configure_reporting_api(token_keypair_paths)
    configure_proxy(cert_paths)
    configure_contrib_portal(settings["template_reports"])

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
