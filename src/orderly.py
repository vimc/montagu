from subprocess import run

import os
import os.path
import paths

import versions
from docker_helpers import get_image_name, docker_cp
from service import orderly_volume_name

from settings import get_secret, save_secret
from service import orderly_volume_name

orderly_ssh_keypath = ""

def create_orderly_store(settings):
    print("Creating orderly store")
    image = get_image_name("montagu-orderly", versions.reports)
    run(["docker", "pull", image], check=True)
    if settings["initial_data_source"] == "restore":
        restore_orderly_store()
    else:
        configure_orderly_store(settings)

def restore_orderly_store():
    print("Restoring orderly permissions")
    args = ["docker", "run", "--rm", "-d",
            "--entrypoint", "chmod",
            "--name", "orderly_setup",
            "-v", orderly_volume_name + ":/orderly",
            get_image_name("montagu-orderly", versions.reports),
            "600", "/orderly/.ssh/id_rsa"]
    run(args)

def configure_orderly_store(settings):
    clone = settings['clone_reports']
    use_real_passwords = settings['use_real_passwords']

    ssh = orderly_prepare_ssh(clone)
    envir = orderly_prepare_envir(use_real_passwords)

    container = "orderly_setup"
    args = ["docker", "run", "--rm", "-d",
            "--entrypoint", "sleep",
            "--name", container,
            "-v", orderly_volume_name + ":/orderly",
            get_image_name("montagu-orderly", versions.reports),
            "infinity"]
    run(args, check = True)

    try:
        if clone:
            print("creating orderly store by cloning montagu-reports")
            # NOTE: Do this _before_ clone, or we can't do the clone
            # as credentials are not found
            docker_cp(ssh, container, "/orderly")
            docker_cp(envir, container, "/orderly")
            run(["docker", "exec", container, "montagu-reports-clone"],
                check = True)
        else:
            print("creating empty orderly store")
            run(["docker", "exec", container, "/usr/bin/orderly_init", "/orderly"],
                check = True)
            # NOTE: Do this _after_ init, or we can't do the
            # initialisation as directory not empty
            docker_cp(ssh, container, "/orderly")
            docker_cp(envir, container, "/orderly")
    finally:
        run(["docker", "stop", "-t0", container])

def orderly_prepare_ssh(clone_reports):
    ssh = paths.orderly + "/.ssh"
    if not os.path.exists(ssh):
        print("preparing orderly ssh")
        os.makedirs(ssh)
        if clone_reports:
            save_secret("vimc-robot/id_rsa.pub", ssh + "/id_rsa.pub")
            save_secret("vimc-robot/id_rsa", ssh + "/id_rsa")
            os.chmod(ssh + "/id_rsa", 0o600)
            with open(ssh + "/known_hosts", 'w') as output:
                run(["ssh-keyscan", "github.com"], stdout = output, check = True)
    return ssh

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
    with open(dest, 'w') as output:
        for e in envir:
            output.write(e + '\n')
    return dest
