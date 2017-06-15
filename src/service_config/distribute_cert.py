import shutil
from os.path import join

from certificates import extract_certificates, cert_dir
from docker_helpers import docker_cp
from service import service


def add_certificate_to_nginx_containers(keystore_password):
    print("Distributing certificate to nginx-based containers")
    cert_paths = extract_certificates(keystore_password)
    try:
        print("- Adding certificate to contrib container")
        add_certificate(service.contrib, cert_paths, "/etc/montagu/webapps")

        print("- Adding certificate to admin container")
        add_certificate(service.admin, cert_paths, "/etc/montagu/webapps")

        print("- Adding certificate to reverse-proxy container")
        add_certificate(service.proxy, cert_paths, "/etc/montagu/proxy")
    finally:
        print("- Deleting unencrypted certificates")
        shutil.rmtree(cert_dir)


def add_certificate(container, cert_paths, path):
    container.exec_run("mkdir -p {}".format(path))
    docker_cp(cert_paths['certificate'], container.name, join(path, "certificate.pem"))
    docker_cp(cert_paths['key'], container.name, join(path, "ssl_key.pem"))
