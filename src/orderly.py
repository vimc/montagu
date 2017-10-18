from subprocess import run

import os
import os.path
import paths

import versions
from docker_helpers import get_image_name, docker_cp
from service import orderly_name, orderly_volume_name

from settings import get_secret, save_secret
from service import orderly_volume_name

orderly_ssh_keypath = ""

def create_orderly_store(settings):
    print("Creating orderly store")
    image = get_image_name("montagu-orderly", versions.orderly)
    run(["docker", "pull", image], check=True)
    if settings["initial_data_source"] == "restore":
        restore_orderly_store()
    else:
        configure_orderly_store(settings)
    print("Sending orderly go signal")
    args = ["docker", "exec", orderly_name, "touch", ".orderly_go"]
    run(args)

def restore_orderly_store():
    print("Restoring orderly permissions")
    args = ["docker", "exec", orderly_name,
            "chmod", "600", "/orderly/.ssh/id_rsa"]
    run(args)

def configure_orderly_envir(settings):
    envir = orderly_prepare_envir(settings['use_real_passwords'])
    docker_cp(envir, orderly_name, "/orderly")

def configure_orderly_store(settings):
    if settings['clone_reports']:
        print("creating orderly store by cloning montagu-reports")
        cmd = ["git", "-C", "/orderly", "clone",
                "git@github.com:vimc/montagu-reports.git"]
    else:
        print("creating empty orderly store")
        cmd = ["/usr/bin/orderly_init", "/orderly"]
    run(["docker", "exec", orderly_name] + cmd, check = True)

def configure_orderly_ssh(settings):
    needs_ssh = settings['clone_reports'] or \
                settings['initial_data_source'] == 'restore'
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
    docker_cp(ssh, orderly_name, "/root/.ssh")

def orderly_prepare_envir(use_real_passwords):
    print("preparing orderly configuration")
    dest = paths.orderly + "/orderly_envir.yml"
    # TODO: perhaps user_configs can be used to get these?
    if use_real_passwords:
        user = "orderly"
        password = get_secret("database/users/orderly", "password")
    else:
        user = "vimc"
        password = "changeme"
    envir = [
        "MONTAGU_PASSWORD: {password}".format(password = password),
        "MONTAGU_HOST: support.montagu.dide.ic.ac.uk",
        "MONTAGU_PORT: 5432",
        "MONTAGU_USER: {user}".format(user = user)]
    if not os.path.exists(paths.orderly):
        os.makedirs(paths.orderly)
    with open(dest, 'w') as output:
        for e in envir:
            output.write(e + '\n')
    return dest
