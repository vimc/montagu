from os import mkdir
from os.path import join, isfile

import paths
from cert_tool import run_cert_tool
from docker_helpers import docker_cp
from settings import get_secret

api_db_user = "api"


def configure_api(service, db_password: str, keypair_paths, hostname, send_emails: bool):
    config_path = "/etc/montagu/api/"
    container = service.api
    print("Configuring API")
    service.api.exec_run("mkdir -p " + config_path)

    print("- Injecting token signing keypair into container")
    service.api.exec_run("mkdir -p " + join(config_path, "token_key"))
    docker_cp(keypair_paths['private'], container.name, join(config_path, "token_key/private_key.der"))
    docker_cp(keypair_paths['public'], container.name, join(config_path, "token_key/public_key.der"))

    print("- Injecting settings into container")
    generate_api_config_file(service, config_path, db_password, hostname,
                             send_emails)

    print("- Sending go signal to API")
    service.api.exec_run("touch {}/go_signal".format(config_path))


def configure_reporting_api(service, keypair_paths):
    config_path = "/etc/montagu/reports_api/"
    container = service.reporting_api
    print("Configuring reporting API")
    container.exec_run("mkdir -p " + config_path)

    print("- Setting Orderly volume location")
    add_property(container, config_path, "orderly.root", "/orderly/")

    print("- Injecting public key for token verification into container")
    container.exec_run("mkdir -p " + join(config_path, "token_key"))
    docker_cp(keypair_paths['public'], container.name, join(config_path, "token_key/public_key.der"))

    print("- Sending go signal to reporting API")
    container.exec_run("touch {}/go_signal".format(config_path))


def add_property(container, config_path, key, value):
    path = "{}/config.properties".format(config_path)
    container.exec_run("touch {}".format(path))
    container.exec_run('echo "{key}={value}" >> {path}'.format(key=key, value=value, path=path))


def get_token_keypair():
    print("Generating token signing keypair")
    run_cert_tool("gen-keypair", paths.token_keypair, args=['/working'])
    result = {
        "private": join(paths.token_keypair, "private_key.der"),
        "public": join(paths.token_keypair, "public_key.der")
    }
    if (not isfile(result['private'])) or (not isfile(result['public'])):
        raise Exception("Obtaining token keypair failed: Missing file(s) in " + paths.token_keypair)
    return result


def generate_api_config_file(service, config_path, db_password: str, hostname: str, send_emails: bool):
    mkdir(paths.config)
    config_file_path = join(paths.config, "config.properties")
    public_url = "https://{}/api".format(hostname)
    print(" - Public URL: " + public_url)
    api_name = service.container_name("api")

    with open(config_file_path, "w") as file:
        print("db.username={}".format(api_db_user), file=file)
        print("db.password={}".format(db_password), file=file)
        print("app.url={}".format(public_url), file=file)
        configure_email(file, send_emails)

    docker_cp(config_file_path, api_name, join(config_path, "config.properties"))


def configure_email(file, send_emails: bool):
    if send_emails:
        password = get_secret("email/password")
        print("email.mode=real", file=file)
        print("email.password=" + password, file=file)
