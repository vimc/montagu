#!/usr/bin/env python3
import webbrowser
from os import chdir, geteuid
from os.path import abspath, dirname
from time import sleep

import bb8_backup
import data_import
import database
import paths
import orderlyweb_cli
from ascii_art import print_ascii_art
from certificates import get_ssl_certificate
from cli import add_test_users, add_user
from git import git_check
from service import MontaguService
from service_config import configure_api, configure_proxy, \
    configure_contrib_portal, configure_static_server, configure_task_queue
from service_config.api_config import get_token_keypair
from settings import get_settings, get_secret
from last_deploy import last_deploy_update
from notify import Notifier
from subprocess import run

def _deploy():
    print_ascii_art()
    print("Beginning Montagu deploy")

    settings = get_settings()
    service = MontaguService(settings)
    status = service.status
    volume_present = service.db_volume_present
    is_first_time = (status is None) and (not volume_present)
    if is_first_time:
        print("Montagu not detected: Beginning new deployment")
    else:
        print("Montagu status: {}. "
              "Data volume present: {}".format(status, volume_present))

    notifier = Notifier(settings['notify_channel'])

    # Check that the deployment environment is clean enough
    version = git_check(settings)

    deploy_str = "montagu {} (`{}`) on `{}`".format(
        version['tag'] or "(untagged)", version['sha'][:7],
        settings['instance_name'])

    notifier.post("*Starting* deploy of " + deploy_str)

    # Pull images
    service.pull()

    # If Montagu is running, back it up before tampering with it
    if status == "running":
        if settings["bb8_backup"]:
            bb8_backup.backup()

    # Stop Montagu if it is running
    # (and delete data volume if persist_data is False)
    if not is_first_time:
        notifier.post("*Stopping* previous montagu "
                      "on `{}` :hand:".format(settings['instance_name']))
        service.stop()

    # Schedule backups
    if settings["bb8_backup"]:
        bb8_backup.schedule()

    # BB8 restore
    data_exists = (not is_first_time) and service.settings["persist_data"]
    if settings["initial_data_source"] == "bb8_restore":
        data_update = service.settings["update_on_deploy"] and \
                      not service.settings["bb8_backup"]
        if data_exists and not data_update:
            print("Skipping bb8 restore: 'persist_data' is set, "
                  "and this is not a first-time deployment")
        else:
            print("Running bb8 restore (while service is stopped)")
            bb8_backup.restore()

    # Start Montagu again
    service.start()
    try:
        print("Configuring Montagu")
        configure_montagu(service, data_exists)

        print("Starting Montagu metrics")
        service.start_metrics()

        print("Montagu metrics started")

    except Exception as e:
        print("An error occurred before deployment could be completed:")
        print(e)
        print("\nYou may need to call ./stop.py before redeploying.")
        try:
            notifier.post("*Failed* deploy of " + deploy_str + " :bomb:")
        except:
            pass
        raise

    try:
        print("Copying public data vis tool")
        copy_vis_tool()
        print("Copied public data vis tool")
    except Exception as e:
        print("An error occurred when copying public data vis tool:")
        print(e)

    if settings["add_test_user"] is True:
        print("Adding tests users")
        add_test_users()

    last_deploy_update(version)
    notifier.post("*Completed* deploy of " + deploy_str + " :shipit:")

    print("Finished deploying Montagu")
    if settings["open_browser"]:
        sleep(1)
        webbrowser.open("https://localhost:{}/".format(settings["port"]))


def configure_montagu(service, data_exists):
    # Do things to the database
    if data_exists:
        print("Skipping data import: 'persist_data' is set, "
              "and this is not a first-time deployment")
    else:
        data_import.do(service)

    passwords = database.setup(service)

    # Push secrets into containers
    cert_paths = get_ssl_certificate(service.settings["certificate"])
    token_keypair_paths = get_token_keypair()

    is_prod = service.settings["password_group"] == 'production'
    configure_api(service, passwords['api'], token_keypair_paths,
                  service.settings["hostname"], is_prod,
                  service.settings["orderly_web_api_url"],
                  service.container_name("flower"))

    task_queue_user = "MONTAGU_TASK_QUEUE"
    task_queue_email = "montagu-task@imperial.ac.uk"
    if service.settings["use_real_diagnostic_reports"]:
        task_queue_password = get_secret(
            "task-queue-user/{}".format(service.settings["instance_name"]),
            "password")
    else:
        task_queue_password = "password"

    print("Configuring task queue user")
    add_user(task_queue_user, task_queue_user, task_queue_email,
             task_queue_password, service.settings["password_group"])
    orderlyweb_cli.add_user(task_queue_email)
    perms = ["*/reports.read", "*/reports.review", "*/reports.run"]
    orderlyweb_cli.grant_permissions(task_queue_email, perms)

    configure_task_queue(service, task_queue_email, task_queue_password,
                         service.settings["orderly_web_api_url"],
                         service.settings["use_real_diagnostic_reports"],
                         service.settings["email_burden_estimate_uploader"],
                         service.settings["fake_smtp"])

    configure_proxy(service, cert_paths)

    if service.settings["include_guidance_reports"]:
        configure_contrib_portal(service)

    if service.settings["copy_static_files"]:
        configure_static_server(service, token_keypair_paths)

def copy_vis_tool():
    run(["../scripts/copy-vis-tool.sh"], check = True)

def deploy():
    try:
        _deploy()
    finally:
        paths.delete_safely(paths.ssl)
        paths.delete_safely(paths.token_keypair)
        paths.delete_safely(paths.config)
        paths.delete_safely(paths.static)


if __name__ == "__main__":
    if geteuid() == 0:
        raise Exception("Please do not run deploy as root user")
    abspath = abspath(__file__)
    chdir(dirname(abspath))
    deploy()
