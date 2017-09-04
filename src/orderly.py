from subprocess import run

import os
import os.path
import paths

import versions
from docker_helpers import get_image_name, docker_cp
from service import orderly_volume_name

from settings import get_secret, save_secret
from service import orderly_volume_name

# TODO: I don't know how this behaves when doing non-persistent
# volumes for orderly.  Is that even actually posible?  Currently all
# the code is written assuming that there _is_ a persistent volume
# because that's kind of needed (unlike other containers there is no
# persistent process).

orderly_ssh_keypath = ""

def create_orderly_store(settings):
    print("Creating orderly store")
    image = get_image_name("montagu-orderly", versions.reports)
    run(["docker", "pull", image], check=True)
    if settings["initial_data_source"] == "restore":
        restore_orderly_store()
    else:
        configure_orderly_store(True)

def restore_orderly_store():
    print("Restoring orderly permissions")
    args = ["docker", "run", "--rm", "-d",
            "--entrypoint", "chmod",
            "--name", "orderly_setup",
            "-v", orderly_volume_name + ":/orderly",
            get_image_name("montagu-orderly", versions.reports),
            "600", "/orderly/.ssh/id_rsa"]
    run(args)

def configure_orderly_store(clone):
    ssh = orderly_prepare_ssh()
    envir = orderly_prepare_envir()

    container = "orderly_setup"
    args = ["docker", "run", "--rm", "-d",
            "--entrypoint", "sleep",
            "--name", container,
            "-v", orderly_volume_name + ":/orderly",
            get_image_name("montagu-orderly", versions.reports),
            "3600"]
    run(args, check = True)

    try:
        docker_cp(ssh, container, "/orderly")
        docker_cp(envir, container, "/orderly")
        if clone:
            print("creating orderly store by cloning montagu-reports")
            script = "montagu-reports-clone"
        else:
            print("creating empty orderly store")
            script = "/usr/bin/orderly_init"
        # import pdb; pdb.set_trace()
        args = ["docker", "exec", container, script]
        run(args, check = True)

    finally:
        paths.delete_safely(paths.orderly)
        run(["docker", "stop", "-t0", container])

def orderly_prepare_ssh():
    ssh = paths.orderly + "/.ssh"
    if not os.path.exists(ssh):
        print("preparing orderly ssh")
        os.makedirs(ssh)
        save_secret("vimc-robot/id_rsa.pub", ssh + "/id_rsa.pub")
        save_secret("vimc-robot/id_rsa", ssh + "/id_rsa")
        os.chmod(ssh + "/id_rsa", 0o600)
        with open(ssh + "/known_hosts", 'w') as output:
            run(["ssh-keyscan", "github.com"], stdout = output, check = True)
    return ssh

def orderly_prepare_envir():
    print("preparing orderly configuration")
    dest = paths.orderly + "/orderly_envir.yml"
    password = get_secret("database/users/orderly", "password")
    envir = [
        "MONTAGU_PASSWORD: {password}".format(password = password),
        "MONTAGU_HOST: support.montagu.dide.ic.ac.uk",
        "MONTAGU_PORT: 5432",
        "MONTAGU_USER: orderly",
        "VAULTR_AUTH_METHOD: github"]
    with open(dest, 'w') as output:
        for e in envir:
            output.write(e + '\n')
    return dest
