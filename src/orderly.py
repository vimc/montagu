import os
import os.path
from subprocess import run

import paths
from database import VaultPassword
from docker_helpers import docker_cp
from settings import save_secret_to_file, get_secret

orderly_ssh_keypath = ""


def configure_orderly(service, initialise_volume):
    # Run this one first because we might need to use the ssh keys to
    # clone:
    configure_orderly_ssh(service)
    # Then this requires an empty directory:
    source_setting = service.settings["initial_data_source"]
    if initialise_volume and source_setting not in ["restore", "bb8_restore"]:
        print("Setting up orderly store")
        initialise_orderly_store(service)
    # Then set up some passwords
    configure_orderly_envir(service)
    # Ensure the orderly db is in a reasonable state
    args = ["docker", "exec", service.orderly.name,
            "orderly", "rebuild", "--if-schema-changed"]
    run(args, check=True)
    # And we're off
    print("Sending orderly go signal")
    args = ["docker", "exec", service.orderly.name, "touch", "/orderly_go"]
    run(args)


def configure_orderly_envir(service):
    password_group = service.settings['password_group']
    api_server = service.settings['instance_name'].lower()
    # These are the entries in montagu-reports/orderly_config.yml:
    # update here if more are added.
    known = ["science", "uat", "production", "latest"]
    if api_server in known:
        slack_url = '"{}"'.format(
            get_secret("slack/orderly-webhook", field="url"))
    else:
        api_server = "~"
        slack_url = "~"
    fake_annex = service.settings["db_annex_type"] == "fake"
    envir = orderly_prepare_envir(password_group, api_server, slack_url,
                                  fake_annex)
    docker_cp(envir, service.orderly.name, "/orderly")


def initialise_orderly_store(service):
    if service.settings['clone_reports']:
        print("creating orderly store by cloning montagu-reports")
        cmd = ["git", "clone", "git@github.com:vimc/montagu-reports.git",
               "/orderly"]
    else:
        print("creating empty orderly store")
        cmd = ["/usr/bin/orderly_init", "/orderly"]
    run(["docker", "exec", service.orderly.name] + cmd, check=True)


def configure_orderly_ssh(service):
    needs_ssh = service.settings['clone_reports'] or \
                service.settings['initial_data_source'] == 'restore'
    if not needs_ssh:
        return
    ssh = paths.orderly + "/.ssh"
    if not os.path.exists(ssh):
        print("preparing orderly ssh")
        os.makedirs(ssh)
        save_secret_to_file("vimc-robot/id_rsa.pub", ssh + "/id_rsa.pub")
        save_secret_to_file("vimc-robot/id_rsa", ssh + "/id_rsa")
        os.chmod(ssh + "/id_rsa", 0o600)
        with open(ssh + "/known_hosts", 'w') as output:
            run(["ssh-keyscan", "github.com"], stdout=output, check=True)
    docker_cp(ssh, service.orderly.name, "/root/.ssh")


def orderly_prepare_envir(password_group, orderly_api_server, slack_url,
                          fake_annex):
    print("preparing orderly configuration")
    dest = paths.orderly + "/orderly_envir.yml"
    user = "orderly"
    password = VaultPassword(password_group, user).get()
    if fake_annex:
        annex_host = "db_annex"
        annex_port = 5432
    else:
        annex_host = "annex.montagu.dide.ic.ac.uk"
        annex_port = 15432
    annex_password = VaultPassword(password_group, "readonly", True).get()
    envir = [
        "MONTAGU_PASSWORD: {password}".format(password=password),
        "MONTAGU_HOST: db",
        "MONTAGU_PORT: 5432",
        "MONTAGU_USER: {user}".format(user=user),
        "ORDERLY_API_SERVER_IDENTITY: {server}".format(
            server=orderly_api_server),
        "SLACK_URL: {url}".format(url=slack_url),
        "ANNEX_HOST: {host}".format(host=annex_host),
        "ANNEX_PORT: {port}".format(port=annex_port),
        "ANNEX_PASSWORD: {password}".format(password=annex_password)]
    if not os.path.exists(paths.orderly):
        os.makedirs(paths.orderly)
    with open(dest, 'w') as output:
        for e in envir:
            output.write(e + '\n')
    return dest
