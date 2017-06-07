import shutil

from certificates import extract_certificates, cert_dir
from docker_helpers import docker_cp
from service import service


def configure_webapps(keystore_password):
    print("Configuring contribution portal")
    cert_paths = extract_certificates(keystore_password)
    try:
        print("- Adding certificate to contrib container")
        contrib = service.contrib
        contrib.exec_run("mkdir -p /etc/montagu/webapps")
        docker_cp(cert_paths['certificate'], contrib.name, "/etc/montagu/webapps/certificate.pem")
        docker_cp(cert_paths['key'], contrib.name, "/etc/montagu/webapps/ssl_key.pem")
    finally:
        print("- Deleting unencrypted certificates")
        shutil.rmtree(cert_dir)


