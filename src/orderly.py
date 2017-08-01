from subprocess import run

import versions
from docker_helpers import get_image_name
from service import orderly_volume_name


def create_empty_store():
    print("Creating empty Orderly store")
    image = get_image_name("montagu-reports", versions.reports)
    run(["docker", "pull", image], check=True)
    template = "docker run --rm --entrypoint /usr/bin/orderly_init -v {volume}:/orderly {image} /orderly"
    run(template.format(volume=orderly_volume_name, image=image).split(' '), check=True)
