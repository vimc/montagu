import shutil
from os.path import join
from typing import Dict

from docker_helpers import docker_cp


def configure_proxy(service, cert_paths: Dict[str, str]):
    print("Configuring reverse proxy")
    add_certificate_to_proxy(service, cert_paths)


def add_certificate_to_proxy(service, cert_paths: Dict[str, str]):
    print("- Adding certificate to reverse-proxy container")
    add_certificate(service.proxy, cert_paths, "/etc/montagu/proxy")


def add_certificate(container, cert_paths, path):
    container.exec_run("mkdir -p {}".format(path))
    docker_cp(cert_paths['certificate'], container.name, join(path, "certificate.pem"))
    docker_cp(cert_paths['key'], container.name, join(path, "ssl_key.pem"))
    docker_cp(cert_paths['dhparam'], container.name, join(path, "dhparam.pem"))
