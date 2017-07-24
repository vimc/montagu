from os import makedirs
from os.path import join, isfile, abspath
from shutil import copy
from subprocess import run, PIPE

import paths
import versions
from cert_tool import run_cert_tool
from docker_helpers import get_image_name
from settings import save_secret


def get_ssl_certificate(certificate_type: str):
    print("Obtaining SSL certificate")
    makedirs(paths.ssl, exist_ok=True)

    if certificate_type == "production":
        result = production()
    elif certificate_type == "support":
        result = support()
    elif certificate_type == "self_signed_fresh":
        result = self_signed_fresh()
    elif certificate_type == "self_signed":
        result = self_signed()
    else:
        raise Exception("Unsupported certificate type: " + certificate_type)

    if (not isfile(result['certificate'])) or (not isfile(result['key'])):
        raise Exception("Obtaining certificate failed: Missing file(s) in " + paths.ssl)
    return result


def cert_path(type, file):
    return join(paths.certs, type, file)


def self_signed_fresh():
    print("- Generating self-signed certificate")
    run_cert_tool("gen-self-signed", paths.ssl, args=["/working"])
    return {
        "certificate": join(paths.ssl, "certificate.pem"),
        "key": join(paths.ssl, "ssl_key.pem")
    }


def self_signed():
    print("- Using self-signed certificate from repository")
    copy(cert_path("self_signed", "certificate.pem"), paths.ssl)
    copy(cert_path("self_signed", "ssl_key.pem"), paths.ssl)
    return {
        "certificate": join(paths.ssl, "certificate.pem"),
        "key": join(paths.ssl, "ssl_key.pem")
    }


def production():
    print("- Using production certificate (montagu.vaccineimpact.org)")
    return real_certificate("production", "montagu.vaccineimpact.org.crt", "ssl/production")


def support():
    print("- Using support certificate (support.montagu.dide.ic.ac.uk)")
    return real_certificate("support", "support.montagu.crt", "ssl/support")


def real_certificate(local_folder, local_name, vault_path):
    copy(cert_path(local_folder, local_name), paths.ssl)

    key_path = join(paths.ssl, "ssl.key")
    save_secret(vault_path, field="key", output=key_path)

    return {
        "certificate": join(paths.ssl, local_name),
        "key": key_path
    }
