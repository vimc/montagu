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
from docopt import docopt

import sys
import os
import celery

import versions
from docker_helpers import get_image_name, pull


def run_in_teamcity_block(name, work):
    print("##teamcity[blockOpened name='{name}']".format(name=name))
    try:
        work()
    finally:
        print("##teamcity[blockClosed name='{name}']".format(name=name))


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

    run_in_teamcity_block("api_blackbox_tests", work)


def webapp_integration_tests():
    def run_suite(portal, version):
        image = "vimc/montagu-portal-integration-tests:{version}".format(version=version)
        pull(image)
        run([
            "docker", "run",
            "--rm",
            "--network", "montagu_default",
            "-v", "/opt/teamcity-agent/.docker/config.json:/root/.docker/config.json",
            "-v", "/var/run/docker.sock:/var/run/docker.sock",
            image,
            portal.title()  # Tests expect capitalized first letter, e.g. "Admin"
        ], check=True)

    def work():
        run_suite("admin", versions.admin_portal)
        run_suite("contrib", versions.contrib_portal)        

    run_in_teamcity_block("webapp_integration_tests", work)

def task_queue_integration_tests():
    def work():
        print('running task_queue integration tests', flush=True)

        #REMOVE THESE
        run(["docker", "ps"], check=True)
        run(["docker", "exec", "montagu_task-queue_1", "cat", "config/config.yml"], check=True)
        run(["docker", "exec", "montagu_task-queue_1", "curl", "-d",
        "grant_type=client_credentials", "-H",
        'Content-Type: application/x-www-form-urlencoded', "--user",
        "test.admin@imperial.ac.uk:password", "-X",
        "POST",
        "http://montagu_api_1:8080/v1/authenticate/", "-i", "-L"], check=True)


        app = celery.Celery(broker="pyamqp://guest@localhost//", backend="rpc://")
        print('made app', flush=True)
        sig = "src.task_run_diagnostic_reports.run_diagnostic_reports"
        print("making signature", flush=True)
        signature = app.signature(sig, ["testGroup", "testDisease"])
        print('running task', flush=True)
        versions = signature.delay().get()
        print('versions: ' + str(versions))
        print('assert 1', flush=True)
        assert len(versions) == 1
        print('assert 2', flush=True)
        assert len(versions[0]) == 24
        print('done with task queue', flush=True)


    run_in_teamcity_block("task_queue_integration_tests", work)

def start_orderly_web():
    def add_user(email, image):
        run([
            # "docker", "run", "-v", "demo:/orderly", image, "add-users", email
            "docker", "run", "-v", "orderly_volume:/orderly", image, "add-users", email
        ], check=True)

    def grant_permissions(email, image, permissions="*/users.manage"):
        run([
            #"docker", "run", "-v", "demo:/orderly", image, "grant", email, permissions
            "docker", "run", "-v", "orderly_volume:/orderly", image, "grant", email, permissions
        ], check=True)

    def work():

        cwd =  os.getcwd()

        run(["docker", "volume", "create", "orderly_volume"], check=True)

        orderly_image = get_image_name("orderly.server", "master")
        pull(orderly_image)
        run([
            "docker", "run", "-d",
            # "--entrypoint", "create_orderly_demo.sh",
            "-p", "8321:8321",
            "--network", "montagu_default",
            "-v", "orderly_volume:/orderly",
            "-w", "/orderly",
            "--name", "montagu_orderly_orderly_1",
            orderly_image,
            "--port", "8321", "--go-signal", "/go_signal", "/orderly"
        ], check=True)

        run(["docker", "exec", "montagu_orderly_orderly_1", "Rscript", "-e",
             "orderly:::create_orderly_demo('/orderly')"], check=True)

       #  run(["docker", "exec", "montagu_orderly_orderly_1", "git", "clone", "https://github.com/vimc/orderly-demo", "/orderly"], check=True)

        run(["docker", "exec", "montagu_orderly_orderly_1", "orderly", "rebuild", "--if-schema-changed"], check=True)

        run(["docker", "exec", "montagu_orderly_orderly_1", "touch", "/go_signal"],
            check=True)

        ow_image = get_image_name("orderly-web", "master")
        pull(ow_image)
        run([
            "docker", "run", "-d",
            "-p", "8888:8888",
            "--network", "montagu_default",
            "-v", "orderly_volume:/orderly",
            "-v", cwd+"/container_config/orderlyweb:/etc/orderly/web",
            "--name", "montagu_orderly_web_1",
            ow_image
        ], check=True)

        #run([
        #    "docker", "cp", cwd + "/orderly_data/demo/orderly.sqlite", "montagu_orderly_web_1:/orderly/orderly.sqlite"
        #], check=True)

        ow_migrate_image = get_image_name("orderlyweb-migrate", "master")
        pull(ow_migrate_image)
        run([
            "docker", "run", "--rm",
            "-v", "orderly_volume:/orderly",
            ow_migrate_image
        ], check=True)

        #run(["pip3", "install", "--upgrade", "pip"], check=True)
        #run(["pip3", "install", "orderly-web"], check=True)
        #run(["orderly-web", "start", cwd+"/container_config/orderlyweb"], check=True)

        ow_cli_image = get_image_name("orderly-web-user-cli", "master")
        pull(ow_cli_image)

        #user for api blackbox tests
        add_user("user@test.com", ow_cli_image)
        grant_permissions("user@test.com", ow_cli_image)

        #user for webapp tests
        add_user("test.user@example.com", ow_cli_image)
        grant_permissions("test.user@example.com", ow_cli_image)
        #run([
        #    "docker", "exec", "montagu_orderly_web_1", "touch", "/etc/orderly/web/go_signal"
        #], check=True)

        #permission for task-queue tests
        grant_permissions("test.user@example.com", ow_cli_image, "*/reports.run")


    run_in_teamcity_block("start_orderly_web", work)


if __name__ == "__main__":
    args = docopt(__doc__)
    if args["--run-tests"]:
        if args["--simulate-restart"]:
            # Imitate a reboot of the system
            print("Restarting Docker", flush=True)
            run(["sudo", "/bin/systemctl", "restart", "docker"], check=True)
        print("starting orderly web", flush=True)
        start_orderly_web()
        api_blackbox_tests()
        print("starting task queue tests", flush=True)
        task_queue_integration_tests()
        webapp_integration_tests()
    else:
        print("Warning - these tests should not be run in a real environment. They will destroy or change data.")
        print("To run the tests, run ./tests.py --run-tests")
        exit(-1)
