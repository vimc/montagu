import shutil

from certificates import extract_certificates, cert_dir
from docker_helpers import docker_cp
from service import service


def configure_webapps(keystore_password):
    print("Configuring portals")
    cert_paths = extract_certificates(keystore_password)
    try:
        print("- Adding certificate to contrib container")
        add_certificate(service.contrib_portal, cert_paths)

        print("- Adding certificate to admin container")
        add_certificate(service.admin_portal, cert_paths)
    finally:
        print("- Deleting unencrypted certificates")
        shutil.rmtree(cert_dir)


def add_certificate(container, cert_paths):
    container.exec_run("mkdir -p /etc/montagu/webapps")
    docker_cp(cert_paths['certificate'], container.name, "/etc/montagu/webapps/certificate.pem")
    docker_cp(cert_paths['key'], container.name, "/etc/montagu/webapps/ssl_key.pem")
