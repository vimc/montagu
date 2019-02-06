from docker_helpers import docker_cp
from docker_helpers import copy_between_volumes
from os.path import join


def configure_static_server(service, keypair_paths):
    container = service.static
    print("Configuring static file server")
    docker_cp(keypair_paths['public_pem'], container.name, "/public_key.pem")
    artefacts = get_artefacts("model_review_2019")
    for a in artefacts:
        if len(a) > 0:
            add_artefact_to_static_volume(service, a)


def add_artefact_to_static_volume(service, artefact):
    artefact = artefact.split(",")
    pattern = artefact[0]
    destination = artefact[1]
    path_to_artefacts = join("archive", pattern)
    print("- Copying artefacts from orderly at {path_to_artefacts} to static server at {destination}"
          .format(path_to_artefacts=path_to_artefacts, destination=destination))
    copy_between_volumes(service.volume_name("orderly"), service.volume_name("static"), path_to_artefacts,
                         destination_path=destination)


def get_artefacts(path):
    with open(path) as f:
        value = f.read()
    return [x.strip() for x in value.split("\n") if x]
