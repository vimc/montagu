#!/usr/bin/env python3
# For now hardcoding a bunch of stuff into here given that the
# service restructure is still pending (VIMC-1201)
import docker
from docker_helpers import montagu_registry

def build_vimc_website(ref="origin/i1205"):
    volume_name = "montagu_website_volume"
    d = docker.client.from_env()
    img_name = "{}/vimc-website-builder:i1205".format(montagu_registry)
    img = d.images.pull(img_name)
    volumes = {
        volume_name: {"bind": "/srv/jekyll", "mode": "rw"}
    }
    try:
        res = d.containers.run(img, ["build-site.sh", ref],
                               volumes = volumes, remove = True, tty = True)
    except docker.errors.ContainerError as e:
        res = e

if __name__ == "__main__":
    build_vimc_website()
