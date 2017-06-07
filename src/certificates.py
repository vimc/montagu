from os import makedirs
from os.path import join, isfile, abspath
from subprocess import run, PIPE

import paths
import versions
from docker_helpers import get_image_name

keystore_path = join(paths.ssl, 'keystore')
cert_dir = join(paths.ssl, 'certs')


def get_keystore(certificate_type: str, keystore_password: str):
    print("Obtaining SSL certificate")
    makedirs(paths.ssl, exist_ok=True)

    if certificate_type == "self-signed":
        with open(keystore_path, 'w') as f:
            run_tool("gen-self-signed", args=[keystore_password], stdout=f)
        print("- Generated self-signed certificate")
        return keystore_path
    else:
        raise Exception("Unsupported certificate type: " + certificate_type)


def extract_certificates(keystore_password):
    print("- Retrieving certificates from keystore")
    makedirs(cert_dir, exist_ok=True)

    run_tool("export-as-pem", args=["/working/keystore", "/working/certs", keystore_password], map_volume=True)
    result = {
        "certificate": join(cert_dir, "certificate.pem"),
        "key": join(cert_dir, "ssl_key.pem")
    }

    if (not isfile(result['certificate'])) or (not isfile(result['key'])):
        raise Exception("Certificate extraction failed: Missing file(s) in " + cert_dir)
    return result


def run_tool(mode, args=[], stdout=PIPE, map_volume=False):
    image = get_image_name("montagu-cert-tool", versions.cert_tool)
    command = ["docker", "run", "--rm"]
    if map_volume:
        command += ["-v", "{}:{}".format(abspath(paths.ssl), "/working")]

    command += [image, mode]
    run(command + args, stdout=stdout, stderr=PIPE)
