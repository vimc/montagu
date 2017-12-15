#!/usr/bin/env python3
# For now hardcoding a bunch of stuff into here given that the
# service restructure is still pending (VIMC-1201)
import docker
from docker_helpers import montagu_registry

def build_vimc_website(ref="origin/i1205"):
    volume_name = "montagu_vimc_website_volume"
    d = docker.client.from_env()
    img_name = "{}/vimc-website-builder:i1205".format(montagu_registry)
    print("Pulling website builder image")
    img = d.images.pull(img_name)
    volumes = {
        volume_name: {"bind": "/srv/jekyll", "mode": "rw"}
    }
    # Note: using create/start/wait rather than run because otherwise
    # it's really hard to get the logs on failed build (the python
    # docker package returns only stderr on failure and the error is
    # in stdout)
    container = d.containers.create(img, ["build-site.sh", ref],
                                    volumes = volumes, tty = True)
    print("Building VIMC website")
    container.start()
    if container.wait() != 0:
        print("...failed")
        print(container.logs().decode("utf-8"))
        container.remove()
        raise Exception("Failed to build website")
    container.remove()
    print("...success")

if __name__ == "__main__":
    build_vimc_website()
