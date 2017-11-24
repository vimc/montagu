from subprocess import check_output, run
import os

montagu_registry_local = "docker.montagu.dide.ic.ac.uk:5000"
montagu_registry_hub = "vimc"

# This is really ugly, but the alternative is to alter every call to
# get_image_name and that feels much more invasive right now.
try:
    use_docker_hub = os.environ['MONTAGU_USE_DOCKER_HUB'] == "true"
except KeyError:
    use_docker_hub = False

montagu_registry = montagu_registry_hub if use_docker_hub else montagu_registry_local

def get_image_name(name, version):
    return "{url}/{name}:{version}".format(url=montagu_registry, name=name, version=version)


def docker_cp(src, container, target_path):
    full_target = "{container}:{path}".format(container=container, path=target_path)
    check_output(["docker", "cp", src, full_target])


def pull(image):
    run(["docker", "pull", image], check=True)
