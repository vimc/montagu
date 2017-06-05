import tarfile
import docker
import io
from subprocess import run, PIPE

import versions
from service import service


def get_keystore(client: docker.DockerClient, certificate_type: str, keystore_password: str):
    if certificate_type == "self-signed":
        version = versions.generate_self_signed_cert
        name = "montagu.dide.ic.ac.uk:5000/montagu-generate-self-signed-cert:{}".format(version)
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
    client = docker.from_env()
    keystore_bytes = get_keystore(client, certificate_type, keystore_password)

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



