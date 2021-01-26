#!/usr/bin/env python3
"""Tags images used in a particular release and pushes the tags into
https://hub.docker.com/u/vimc.  Use tag 'latest' to select the most recent
conforming git tag (this will not set things to be the docker 'latest' tag
though).

Usage:
  tag-images.py <version>

"""
import docker
import docopt
from subprocess import run
import os
import re
import git_helpers
from release_tag import get_latest_release_tag, validate_release_tag

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
    "montagu-reverse-proxy": "proxy",
    "montagu-static": "static"
}

registry = "vimc"


class DockerTag:
    def __init__(self, registry, name, version=None):
        self.registry = registry
        self.name = name
        self.version = version

    def __str__(self):
        if self.version:
            return "{}/{}:{}".format(self.registry, self.name, self.version)
        else:
            return "{}/{}".format(self.registry, self.name)

    @property
    def repository(self):
        return "{}/{}".format(self.registry, self.name)

    @classmethod
    def parse(self, raw):
        registry, parts = raw.split("/")
        name, version = parts.split(":")
        return DockerTag(registry, name, version)


def set_image_tag(name, version):
    repo_name = container_repo_map[name]
    sha = git_helpers.get_past_submodule_version(repo_name, version)
    d = docker.client.from_env()
    img = d.images.pull(str(DockerTag(registry, name, sha)))
    tag_and_push(img, registry, name, version)


def set_image_tags(version):
    print("Setting image tags")
    for name in container_repo_map.keys():
        print("  - " + name)
        set_image_tag(name, version)


# NOTE: Using subprocess here and not the python docker module because
# the latter does not support streaming as nicely as the CLI
def tag_and_push(img, registry, name, tag):
    t = DockerTag(registry, name, tag)
    img.tag(t.repository, t.version)
    run(["docker", "push", str(t)], check=True)


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

    set_image_tags(version)
