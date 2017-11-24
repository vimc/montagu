#!/usr/bin/env python3
"""Tags images used in a particular release and pushes the tags into
our local docker registry at docker.montagu.dide.ic.ac.uk:5000.  Use
tag 'latest' to select the most recent conforming git tag (this will
not set things to be the docker 'latest' tag though).  If run with the
"publish" option it will also publish images to
https://hub.docker.com/u/vimc

Usage:
  tag-images.py tag [--publish] <version>
  tag-images.py publish <version>

"""
import docker
import docopt
from subprocess import run
import os
import re
import git_helpers
from helpers import get_latest_release_tag, validate_release_tag

# This feels like something we should have elsewhere; it's a map of
# the name of the *repo* (the key here) with the name of the submodule
# *subdirectory* (the value, which then maps onto the docker compose
# container name).  It's easy enough to lift this out later though.
#
# Not currently included are montagu-portal-integration-tests and
# montagu-api-blackbox-tests (both of which version against the api
# submodule).
container_repo_map = {
    "montagu-admin-portal": "admin-portal",
    "montagu-api": "api",
    "montagu-cert-tool": "cert-tool",
    "montagu-cli": "api",
    "montagu-contrib-portal": "contrib-portal",
    "montagu-db": "db",
    "montagu-migrate": "db",
    "montagu-orderly": "orderly",
    "montagu-report-portal": "report-portal",
    "montagu-reporting-api": "reporting-api",
    "montagu-reverse-proxy": "proxy"
}

registry = "docker.montagu.dide.ic.ac.uk:5000"

def set_image_tag(name, version):
    repo_name = container_repo_map[name]
    sha = git_helpers.get_past_submodule_version(repo_name, version)
    d = docker.client.from_env()
    img = d.images.pull("{}/{}:{}".format(registry, name, sha))
    tag_and_push(img, registry, name, version)

def set_image_tags(version):
    print("Setting image tags")
    for name in container_repo_map.keys():
        print("  - " + name)
        set_image_tag(name, version)

def publish_images(version):
    d = docker.client.from_env()
    print("Pushing release to docker hub")
    for name in container_repo_map.keys():
        img = d.images.get("{}/{}:{}".format(registry, name, version))
        tag_and_push(img, "vimc", name, version)

# NOTE: Using subprocess here and not the python docker module because
# the latter does not support streaming as nicely as the CLI
def tag_and_push(img, registry, name, tag):
    repo = "{}/{}".format(registry, name)
    img.tag(repo, tag)
    run(["docker", "push", "{}:{}".format(repo, tag)], check = True)

def get_past_submodule_versions(master_repo_version):
    return {k: get_past_submodule_version(k, master_repo_version)
            for k in os.listdir("submodules")}

if __name__ == "__main__":
    args = docopt.docopt(__doc__)
    version = args["<version>"]
    if version == "latest":
        version = get_latest_release_tag()
    else:
        validate_release_tag(version)
    if args["tag"]:
        set_image_tags(version)
        if args["--publish"]:
            publish_images(version)
    elif args["publish"]:
        publish_images(version)
