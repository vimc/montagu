import io
import tarfile

from service import service


def configure_api(db_password: str, keystore_path: str, keystore_password: str):
    print("Configuring API")
    # do something with the database password

    print("- Adding certificate to API container")
    api = service.api
    api.exec_run("mkdir -p /etc/montagu/api")
    with io.BytesIO() as out:
        archive = tarfile.open(mode='w', fileobj=out)
        archive.add(keystore_path, 'keystore')
        tar_bytes = out.getvalue()
    api.put_archive("/etc/montagu/api/", tar_bytes)



