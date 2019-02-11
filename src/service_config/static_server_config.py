from docker_helpers import docker_cp
from docker_helpers import copy_between_volumes
from os.path import join
import os
from pathlib import Path
import paths
from settings import save_secret_to_file
from subprocess import run

montagu_root = str(Path(__file__).parent.parent.parent)


def configure_static_server(service, keypair_paths):
    container = service.static
    print("Configuring static file server")
    docker_cp(keypair_paths['public_pem'], container.name, "/public_key.pem")
    configure_static_files(service)


def configure_static_files(service):
    initialise_static_volume(service)
    static_file_configs = get_static_file_configs(join(montagu_root, "static"))
    for config in static_file_configs:
        print("Found static file config at {}".format(config["file_path"]))
        artefacts = get_artefacts(config["file_path"])
        for a in artefacts:
            if len(a) > 0:
                add_artefact_to_static_volume(service, a, config["path_prefix"])


def add_artefact_to_static_volume(service, artefact, path_prefix):
    artefact = artefact.split(",")
    path_to_artefacts = join("archive", artefact[0])
    destination = join(path_prefix, artefact[1])
    print("- Copying artefacts from orderly at {path_to_artefacts} to static server at {destination}"
          .format(path_to_artefacts=path_to_artefacts, destination=destination))
    copy_between_volumes(service.volume_name("orderly"), service.volume_name("static"), path_to_artefacts,
                         destination_path=destination)


def get_static_file_configs(path):
    all_files_path = []
    for (dirpath, dirnames, filenames) in os.walk(path):
        for f in filenames:
            all_files_path.append({"file_path": os.path.join(dirpath, f),
                                   "path_prefix": os.path.relpath(dirpath, path)})
    return all_files_path


def get_artefacts(path):
    with open(path) as f:
        value = f.read()
    return [x.strip() for x in value.split("\n") if x]


def configure_static_ssh(service):
    needs_ssh = service.settings['clone_reports'] or \
                service.settings['initial_data_source'] == 'restore'
    if not needs_ssh:
        return
    ssh = paths.static + "/.ssh"
    if not os.path.exists(ssh):
        print("Preparing static ssh")
        os.makedirs(ssh)
        save_secret_to_file("vimc-robot/id_rsa.pub", ssh + "/id_rsa.pub")
        save_secret_to_file("vimc-robot/id_rsa", ssh + "/id_rsa")
        os.chmod(ssh + "/id_rsa", 0o600)
        with open(ssh + "/known_hosts", 'w') as output:
            run(["ssh-keyscan", "github.com"], stdout=output, check=True)
    return os.path.abspath(ssh)


def initialise_static_volume(service):
    cmd = ["rm -rf /www/*",
           "git clone --depth=1 git@github.com:vimc/montagu-static-files.git",
           "mv montagu-static-files/www/* /www"]
    ssh_path = configure_static_ssh(service)
    run(["docker", "run", "--rm", "-i", "-t",
         "-v", "{}:/root/.ssh:ro".format(ssh_path),
         "-v", "{}:/www".format(service.volume_name("static")),
         "alpine/git",
         "ash",
         "-c",
         " && ".join(cmd)
         ], check=True)
