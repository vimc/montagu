#!/usr/bin/env python3
from subprocess import run

import sys

import versions
from docker_helpers import get_image_name


def run_in_teamcity_block(name, work):
    print("##teamcity[blockOpened name='{name}']".format(name=name))
    try:
        work()
    finally:
        print("##teamcity[blockClosed name='{name}']".format(name=name))


def api_blackbox_tests():
    def work():
        image = get_image_name("montagu-api-blackbox-tests", versions.api)
        run([
            "docker", "run",
            "--rm",
            "--network", "montagu_default",
            "-v", "montagu_emails:/tmp/montagu_emails",
            image
        ], check=True)

    run_in_teamcity_block("api_blackbox_tests", work)


def webapp_integration_tests():
    def work():
        image = get_image_name("montagu-portal-integration-tests", "local")
        run([
            "docker", "run",
            "--rm",
            "--network", "montagu_default",
            "-v", "/var/run/docker.sock:/var/run/docker.sock",
            image
        ], check=True)

    run_in_teamcity_block("webapp_integration_tests", work)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--run-tests":
        api_blackbox_tests()
        webapp_integration_tests()
    else:
        print("Warning - these tests should not be run in a real environment. They will destroy or change data.")
        print("To run the tests, run ./tests.py --run-tests")
        exit(-1)
