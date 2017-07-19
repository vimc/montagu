from os import makedirs
from os.path import join, isfile, abspath
from shutil import copy
from subprocess import run, PIPE

import paths
import versions
from cert_tool import run_cert_tool
from docker_helpers import get_image_name


def get_ssl_certificate(certificate_type: str):
    print("Obtaining SSL certificate")
    makedirs(paths.ssl, exist_ok=True)

    if certificate_type == "self_signed_fresh":
        run_cert_tool("gen-self-signed", paths.ssl, args=["/working"])
        print("- Generated self-signed certificate")
    elif certificate_type == "self_signed":
        print("- Using self-signed certificate from repository")
        copy(join("self_signed", "certificate.pem"), paths.ssl)
        copy(join("self_signed", "ssl_key.pem"), paths.ssl)
    else:
        raise Exception("Unsupported certificate type: " + certificate_type)

    result = {
        "certificate": join(paths.ssl, "certificate.pem"),
        "key": join(paths.ssl, "ssl_key.pem")
    }
    if (not isfile(result['certificate'])) or (not isfile(result['key'])):
        raise Exception("Obtaining certificate failed: Missing file(s) in " + paths.ssl)
    return result
