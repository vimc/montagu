from os import makedirs
from subprocess import run, DEVNULL

import pystache as pystache

from database import prepare_db_for_import
from last_deploy import last_restore_update

finished_setup = False


def configure(service):
    with open("../backup/configs/production/config.json", 'r') as f:
        template = f.read()
    config = pystache.render(template, {
        "s3_bucket": service.settings["backup_bucket"],
        "db_container": service.container_name("db"),
        "orderly_volume": service.volume_name("orderly")
    })
    makedirs("/etc/montagu/backup", exist_ok=True)
    with open("/etc/montagu/backup/config.json", 'w') as f:
        f.write(config)


def needs_setup():
    return run("../backup/needs-setup.sh", stdout=DEVNULL,
               stderr=DEVNULL).returncode == 1


def setup(service):
    if needs_setup():
        print("- Configuring and installing backup service")
        configure(service)
        run("../backup/setup.sh", check=True)


def backup(service):
    # Note, it is safe to run the backup on a running system, as pg_dump uses TRANSACTION ISOLATION LEVEL SERIALIZABLE
    # i.e. The backup will only see transactions that were committed before the isolation level was set.
    # So we will get a consistent backup, even if changes are being made.
    print("Performing backup")
    setup(service)
    run("../backup/backup.py", check=True)


def schedule(service):
    print("Scheduling backup")
    setup(service)
    run(["../backup/schedule.py", "--no-immediate-backup"], check=True)


def restore(service):
    print("Restoring from remote backup")
    setup(service)
    ## Because of the annex work we need to ensure that users *exist*
    ## here at this point and do that just before restoring the
    ## database.  This is all a bit nasty really.
    prepare_db_for_import(service)
    run(["../backup/restore.py"], check=True)
    last_restore_update()
