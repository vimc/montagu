from subprocess import run

import os
import os.path
import paths

from docker_helpers import docker_cp
from settings import get_secret, save_secret
from database import VaultPassword

orderly_ssh_keypath = ""

def configure_orderly(service, initialise_volume):
    ## Run this one first because we might need to use the ssh keys to
    ## clone:
    configure_orderly_ssh(service)
    ## Then this requires an empty directory:
    if initialise_volume and service.settings["initial_data_source"] != "restore":
        print("Setting up orderly store")
        initialise_orderly_store(service)
    ## Then set up some passwords
    configure_orderly_envir(service)
    ## And we're off
    print("Sending orderly go signal")
    args = ["docker", "exec", service.orderly.name, "touch", "/orderly_go"]
    run(args)

def configure_orderly_envir(service):
    envir = orderly_prepare_envir(service.settings['password_group'])
    docker_cp(envir, service.orderly.name, "/orderly")

def initialise_orderly_store(service):
    if service.settings['clone_reports']:
        print("creating orderly store by cloning montagu-reports")
        cmd = ["git", "clone", "git@github.com:vimc/montagu-reports.git",
               "/orderly"]
    else:
        print("creating empty orderly store")
        cmd = ["/usr/bin/orderly_init", "/orderly"]
    run(["docker", "exec", service.orderly.name] + cmd, check = True)

def configure_orderly_ssh(service):
    needs_ssh = service.settings['clone_reports'] or \
                service.settings['initial_data_source'] == 'restore'
    if not needs_ssh:
        return
    ssh = paths.orderly + "/.ssh"
    if not os.path.exists(ssh):
        print("preparing orderly ssh")
        os.makedirs(ssh)
        save_secret("vimc-robot/id_rsa.pub", ssh + "/id_rsa.pub")
        save_secret("vimc-robot/id_rsa", ssh + "/id_rsa")
        os.chmod(ssh + "/id_rsa", 0o600)
        with open(ssh + "/known_hosts", 'w') as output:
            run(["ssh-keyscan", "github.com"], stdout = output, check = True)
    docker_cp(ssh, service.orderly.name, "/root/.ssh")

def orderly_prepare_envir(password_group):
    print("preparing orderly configuration")
    dest = paths.orderly + "/orderly_envir.yml"
    user = "orderly"
    password = VaultPassword(password_group, user).get()
    envir = [
        "MONTAGU_PASSWORD: {password}".format(password = password),
        "MONTAGU_HOST: db",
        "MONTAGU_PORT: 5432",
        "MONTAGU_USER: {user}".format(user = user)]
    if not os.path.exists(paths.orderly):
        os.makedirs(paths.orderly)
    with open(dest, 'w') as output:
        for e in envir:
            output.write(e + '\n')
    return dest
