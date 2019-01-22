#!/usr/bin/env python3
"""Deploy montagu

Usage:
  deploy.py [--docker-hub] [<version>]

Options:
  --docker-hub   Use hub.docker.com (rather than docker.montagu.dide.ic.uk)
"""
import docopt
import os
from subprocess import run
import sys
sys.path.append("scripts/release")
from release_tag import get_latest_release_tag, validate_release_tag

def checkout(version):
    print("checking out version {}".format(version))
    run(["git", "checkout", version], check = True)
    run(["git", "submodule", "update", "--recursive"], check = True)

def deploy():
    run("./src/deploy.py", check = True)

def get_version_from_user():
    latest = get_latest_release_tag()
    prompt = "Which tag do you want to deploy? [{}] ".format(latest)
    tag = input(prompt) or latest
    validate_release_tag(tag)
    return tag

if __name__ == "__main__":
    if os.geteuid() == 0:
        raise Exception("Please do not run deploy as root user")
    args = docopt.docopt(__doc__)
    version = args["<version>"] or get_version_from_user()
    if args["--docker-hub"]:
        os.environ["MONTAGU_USE_DOCKER_HUB"] = "true"
    checkout(version)
    deploy()
