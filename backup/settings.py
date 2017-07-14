import json
import os
from os.path import join, isfile

from subprocess import check_output

root_path = "/etc/montagu/backup"
config_path = join(root_path, "config.json")
list_path = join(root_path, "paths.list")
secrets_path = join(root_path, "secrets.json")

log_dir = '/var/log/duplicati'


class Settings:
    def __init__(self):
        with open(config_path, 'r') as f:
            config = json.load(f)
        with open(secrets_path, 'r') as f:
            secrets = json.load(f)
        with open(list_path, 'r') as f:
            paths = [path.strip() for path in f.readlines() if path]

        self.remote_url = "s3://{bucket}".format(bucket=config["s3_bucket"])
        self.encrypted = config["encrypted"]
        self.secrets = secrets
        self.paths = paths


def shared_args(settings):
    secrets = settings.secrets
    args = [
        "--aws_access_key_id={aws_access_key_id}".format(**secrets),
        "--aws_secret_access_key={aws_secret_access_key}".format(**secrets),
        "--use-ssl"
    ]
    if settings.encrypted:
        args += ["--passphrase={passphrase}".format(**secrets)]
    else:
        args += ["--no-encryption=true"]
    return args


def load_settings():
    return Settings()


def get_secret(name):
    path = "secret/backup/{}".format(name)
    return check_output(["vault", "read", "-field=value", path]).decode('utf-8')


def save_secrets(get_passphrase):
    if not isfile(secrets_path):
        secrets = {
            "aws_access_key_id": get_secret("aws_access_key_id"),
            "aws_secret_access_key": get_secret("aws_secret_access_key"),
        }
        if get_passphrase:
            secrets["passphrase"] = get_secret("passphrase")

        with open(secrets_path, 'a'):  # Create file if does not exist
            pass
        os.chmod(secrets_path, 0o600)
        with open(secrets_path, 'w') as f:
            json.dump(secrets, f)
