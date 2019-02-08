from docker_helpers import docker_cp
from docker_helpers import copy_between_volumes
from os.path import join
import os
from pathlib import Path

montagu_root = str(Path(__file__).parent.parent.parent)


def configure_static_server(service, keypair_paths):
    container = service.static
    print("Configuring static file server")
    docker_cp(keypair_paths['public_pem'], container.name, "/public_key.pem")
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
