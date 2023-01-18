#!/usr/bin/env python3

"""
Run integration tests on a deployed Montagu instance

Usage:
  test.py --run-tests [--simulate-restart]

Options:
  --run-tests         Required. This is included to prevent accidentally
                      running the tests in a live environment.
  --simulate-restart  Restart the Docker daemon before running the tests,
                      to simulate recovery from a system reboot.
"""

from subprocess import run

from YTClient.YTClient import YTClient
from YTClient.YTDataClasses import Command
from docopt import docopt

import os
import celery
import requests

import versions
from docker_helpers import get_image_name, pull


def run_in_buildkite_block(name, work):
    # Always do a trailing newline, in case we have a partial line before.
    print("")
    print("--- " + name)
    work()


def api_blackbox_tests():
    def work():
        image = get_image_name("montagu-api-blackbox-tests", versions.api)
        pull(image)
        run([
            "docker", "run",
            "--rm",
            "--network", "montagu_default",
            "-v", "montagu_emails:/tmp/montagu_emails",
            image
        ], check=True)

    run_in_buildkite_block("api_blackbox_tests", work)


def webapp_integration_tests():
    def run_suite(portal, version):
        image = "vimc/montagu-portal-integration-tests:{version}".format(
            version=version)
        pull(image)
        run([
            "docker", "run",
            "--rm",
            "--network", "montagu_default",
            "-v",
            "/var/lib/buildkite-agent/.docker/config.json:/root/.docker/config.json",
            "-v", "/var/run/docker.sock:/var/run/docker.sock",
            image,
            portal.title()
            # Tests expect capitalized first letter, e.g. "Admin"
        ], check=True)

    def work():
        run_suite("admin", versions.admin_portal)
        run_suite("contrib", versions.contrib_portal)

    run_in_buildkite_block("webapp_integration_tests", work)


def task_queue_integration_tests():
    def work():
        print("Running task queue integration tests")
        yt = YTClient('https://mrc-ide.myjetbrains.com/youtrack/',
                      token=os.environ["YOUTRACK_TOKEN"])
        app = celery.Celery(broker="redis://localhost//",
                            backend="redis://")
        sig = "run-diagnostic-reports"
        args = ["testGroup", "testDisease", "testTouchstone-1",
                "2020-11-04T12:21:15", "no_vaccination"]
        signature = app.signature(sig, args)
        versions = signature.delay().get()
        assert len(versions) == 1
        # check expected notification email was sent to fake smtp server
        emails = requests.get("http://localhost:1080/api/emails").json()
        assert len(emails) == 1
        s = "VIMC diagnostic report: testTouchstone-1 - testGroup - testDisease"
        assert emails[0]["subject"] == s
        assert emails[0]["to"]["value"][0][
                   "address"] == "minimal_modeller@example.com"  #
        issues = yt.get_issues("tag: {}".format("testTouchstone-1"))
        assert len(issues) == 1
        yt.run_command(Command(issues, "delete"))

    run_in_buildkite_block("task_queue_integration_tests", work)


def start_orderly_web():
    def add_user(email, image):
        run([
            "docker", "run", "-v", "orderly_volume:/orderly", image,
            "add-users", email
        ], check=True)

    def grant_permissions(email, image, permissions):
        run(["docker", "run", "-v", "orderly_volume:/orderly",
             image, "grant", email] + permissions, check=True)

    def work():
        cwd = os.getcwd()

        run(["docker", "volume", "create", "orderly_volume"], check=True)

        run(["docker", "run", "-d",
             "--network", "montagu_default",
             "--name", "redis",
             "redis"], check=True)

        orderly_image = get_image_name("orderly.server", "master")
        pull(orderly_image)
        run([
            "docker", "run", "-d",
            "-p", "8321:8321",
            "--network", "montagu_default",
            "-v", "orderly_volume:/orderly",
            "-w", "/orderly",
            "-e", "REDIS_URL=redis://redis",
            "--name", "montagu_orderly_orderly_1",
            orderly_image,
            "--port", "8321",
            "--go-signal", "/go_signal", "--workers=1", "/orderly",
        ], check=True)

        run(["docker", "exec", "montagu_orderly_orderly_1", "git", "clone",
             "https://github.com/vimc/montagu-task-queue-orderly", "/orderly"],
            check=True)

        run(["docker", "exec", "montagu_orderly_orderly_1", "orderly",
             "rebuild", "--if-schema-changed"], check=True)

        run(["docker", "exec", "montagu_orderly_orderly_1", "touch",
             "/go_signal"],
            check=True)

        ow_image = get_image_name("orderly-web", "mrc-3916")
        pull(ow_image)
        run([
            "docker", "run", "-d",
            "-p", "8888:8888",
            "--network", "montagu_default",
            "-v", "orderly_volume:/orderly",
            "-v", cwd + "/container_config/orderlyweb:/etc/orderly/web",
            "--name", "montagu_orderly_web_1",
            ow_image
        ], check=True)

        run(["docker", "exec", "montagu_orderly_web_1", "touch",
             "/etc/orderly/web/go_signal"],
            check=True)

        ow_migrate_image = get_image_name("orderlyweb-migrate", "master")
        pull(ow_migrate_image)
        run([
            "docker", "run", "--rm",
            "-v", "orderly_volume:/orderly",
            ow_migrate_image
        ], check=True)

        ow_cli_image = get_image_name("orderly-web-user-cli", "master")
        pull(ow_cli_image)

        # user for api blackbox tests
        add_user("user@test.com", ow_cli_image)
        grant_permissions("user@test.com", ow_cli_image, ["*/users.manage"])

        # add task q user
        add_user("montagu-task@imperial.ac.uk", ow_cli_image)
        grant_permissions("montagu-task@imperial.ac.uk", ow_cli_image,
                          ["*/reports.run", "*/reports.review",
                           "*/reports.read"])

        # user for webapp tests
        add_user("test.user@example.com", ow_cli_image)
        grant_permissions("test.user@example.com", ow_cli_image,
                          ["*/users.manage"])

    run_in_buildkite_block("start_orderly_web", work)


if __name__ == "__main__":
    args = docopt(__doc__)
    if args["--run-tests"]:
        if args["--simulate-restart"]:
            # Imitate a reboot of the system
            print("Restarting Docker", flush=True)
            run(["sudo", "/bin/systemctl", "restart", "docker"], check=True)
        start_orderly_web()
        task_queue_integration_tests()
        api_blackbox_tests()
        webapp_integration_tests()
    else:
        print(
            "Warning - these tests should not be run in a real environment. They will destroy or change data.")
        print("To run the tests, run ./tests.py --run-tests")
        exit(-1)
