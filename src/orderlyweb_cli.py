from docker_helpers import get_image_name, pull
from subprocess import run, PIPE


def cli(command):
    image = get_image_name("orderly-web-user-cli", "master")
    pull(image)
    result = run(["docker", "run", "--rm", "-v",
         "montagu_orderly_volume:/orderly",
         "--network", "montagu_default",
         image] + command, stderr=PIPE, stdout=PIPE)
    print(result.stderr)
    print(result.stdout)
    if result.returncode > 0:
        print(result.args)
        print("Warning: failed to execute command")


def add_user(user):
    cli(["add-users", user])


def grant_permissions(user, permissions):
    cli(["grant", user] + permissions)
