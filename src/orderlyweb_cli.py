from docker_helpers import get_image_name, pull


def cli(command):
    image = get_image_name("orderly-web-user-cli", "master")
    pull(image)
    run(["docker", "run", "--rm", "-v",
         "orderly_volume:/orderly",
         "--network", "montagu_default",
         image] + command, check=True)


def add_user(user):
    cli(["add-users", user])


def grant_permissions(user, permissions):
    cli(["grant", user] + permissions)
