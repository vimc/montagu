from os import makedirs
from subprocess import run

import pystache as pystache
from os.path import isdir

import service

from last_deploy import last_restore_update

finished_setup = False


def configure(settings):
    with open("../backup/configs/production/config.json", 'r') as f:
        template = f.read()
    config = pystache.render(template, {
        "s3_bucket": settings["backup_bucket"],
        "db_container": service.db_name,
        "orderly_volume": service.orderly_volume_name
    })
    makedirs("/etc/montagu/backup", exist_ok=True)
    with open("/etc/montagu/backup/config.json", 'w') as f:
        f.write(config)


def setup(settings):
    global finished_setup
    if not finished_setup:
        print("- Configuring and installing backup service")
        configure(settings)
        run("../backup/setup.sh", check=True)
        finished_setup = True


def backup(settings):
    # Note, it is safe to run the backup on a running system, as pg_dump uses TRANSACTION ISOLATION LEVEL SERIALIZABLE
    # i.e. The backup will only see transactions that were committed before the isolation level was set.
    # So we will get a consistent backup, even if changes are being made.
    print("Performing backup")
    setup(settings)
    run("../backup/backup.py", check=True)


def schedule(settings):
    print("Scheduling backup")
    setup(settings)
    run(["../backup/schedule.py", "--no-immediate-backup"], check=True)


def restore(settings):
    print("Restoring from remote backup")
    setup(settings)
    run(["../backup/restore.py"], check=True)
    last_restore_update()
