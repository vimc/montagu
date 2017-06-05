import io
import tarfile
from subprocess import run, PIPE

import versions
from images import get_image_name
from service import service


def get_keystore(certificate_type: str, keystore_password: str):
    if certificate_type == "self-signed":
        version = versions.generate_self_signed_cert
        name = get_image_name("montagu-generate-self-signed-cert", version)
        p = run([
            "docker", "run",
            "--rm",
            name,
            keystore_password
        ], stdout=PIPE)
        keystore_bytes = p.stdout
        # client.containers.run(name, keystore_password, remove=True)
        print("- Generated self-signed certificate")
        return keystore_bytes
    else:
        raise Exception("Unsupported certificate type: " + certificate_type)


def configure_api(certificate_type: str, db_password: str, keystore_password: str):
    # do something with the database password

    print("Configuring SSL")
    print("- Obtaining SSL certificate")
    keystore_bytes = get_keystore(certificate_type, keystore_password)

    print("- Adding certificate to API container")
    api = service.api
    api.exec_run("mkdir -p /etc/montagu/api")
    with io.BytesIO() as out:
        archive = tarfile.open(mode='w', fileobj=out)
        info = tarfile.TarInfo("keystore")
        info.size = len(keystore_bytes)
        with io.BytesIO(keystore_bytes) as keystore:
            archive.addfile(info, fileobj=keystore)
        tar_bytes = out.getvalue()
    api.put_archive("/etc/montagu/api/", tar_bytes)



