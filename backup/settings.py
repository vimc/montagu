import json
from os.path import join

from subprocess import check_output

root_path = "/etc/montagu/backup"
config_path = join(root_path, "config.json")
list_path = join(root_path, "paths.list")
secrets_path = join(root_path, "secrets.json")

log_dir = '/var/log/duplicati'


def shared_args(secrets):
    return [
        "--aws_access_key_id={aws_access_key_id}".format(**secrets),
        "--aws_secret_access_key={aws_secret_access_key}".format(**secrets),
        "--passphrase={passphrase}".format(**secrets)
    ]


def load_settings():
    with open(config_path, 'r') as f:
        config = json.load(f)
    with open(secrets_path, 'r') as f:
        secrets = json.load(f)
    with open(list_path, 'r') as f:
        paths = [path.strip() for path in f.readlines() if path]

    return {
        "remote_url": "s3://{bucket}".format(bucket=config["s3_bucket"]),
        "secrets": secrets,
        "paths": paths,
    }


def get_secret(name):
    path = "secret/backup/{}".format(name)
    return check_output(["vault", "read", "-field=value", path]).decode('utf-8')


def save_secrets():
    secrets = {
        "passphrase": get_secret("passphrase"),
        "aws_access_key_id": get_secret("aws_access_key_id"),
        "aws_secret_access_key": get_secret("aws_secret_access_key"),
    }
    with open(secrets_path, 'w') as f:
        json.dump(secrets, f)
