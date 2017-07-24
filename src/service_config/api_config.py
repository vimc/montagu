from os.path import join, isfile

import paths
from cert_tool import run_cert_tool
from docker_helpers import docker_cp
from service import service, api_name

config_path = "/etc/montagu/api/"


def configure_api(db_password: str, keypair_paths):
    print("Configuring API")
    service.api.exec_run("mkdir -p " + config_path)

    print("- Injecting token signing keypair into container")
    service.api.exec_run("mkdir -p " + join(config_path, "token_key"))
    docker_cp(keypair_paths['private'], api_name, join(config_path, "token_key/private_key.der"))
    docker_cp(keypair_paths['public'], api_name, join(config_path, "token_key/public_key.der"))

    print("- Injecting db password into container")
    generate_config_file(db_password)

    print("- Sending go signal to API")
    service.api.exec_run("touch {}/go_signal".format(config_path))


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


def generate_config_file(db_password: str):
    config_file_path = "{}/config.properties".format(config_path)
    service.api.exec_run("touch {}".format(config_file_path))
    service.api.exec_run('echo "db.password={}" >> {}'.format(db_password, config_file_path))