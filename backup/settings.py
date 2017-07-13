import json

from subprocess import check_output


def shared_args(secrets):
    return [
        "--aws_access_key_id={aws_access_key_id}".format(**secrets),
        "--aws_secret_access_key={aws_secret_access_key}".format(**secrets),
        "--passphrase={passphrase}".format(**secrets)
    ]


def load_settings():
    with open("/etc/montagu/duplicati/duplicati.json", 'r') as f:
        config = json.load(f)
    with open('/etc/montagu/duplicati/duplicati.list', 'r') as f:
        paths = [path.strip() for path in f.readlines() if path]

    return {
        "remote_url": "s3://{bucket}".format(bucket=config["s3_bucket"]),
        "paths": paths
    }


def get_secret(name):
    path = "secret/backup/{}".format(name)
    return check_output(["vault", "read", "-field=value", path])


def get_secrets():
    return {
        "passphrase": get_secret("passphrase"),
        "aws_access_key_id": get_secret("/aws_access_key_id"),
        "aws_secret_access_key": get_secret("aws_secret_access_key"),
    }