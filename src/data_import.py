from subprocess import check_output

import bb8_backup
import versions
from docker_helpers import docker_cp


def do(service):
    source = service.settings["initial_data_source"]
    print("Running initial data import with mode: {}".format(source))
    if source == "minimal":
        print("- Nothing to do (migrations will insert minimal data)")
    elif source == "bb8_restore":
        print("Nothing to do: Already ran bb8 before starting services")
    else:
        raise Exception("Unknown mode '{}'".format(source))


def import_dump(db, dump_path):
    print("- Copying {} to DB container and importing into database".format(dump_path))
    target_path = "/tmp/import.dump"
    docker_cp(dump_path, db.name, target_path)
    check_output(["docker", "exec", db.name, "/montagu-bin/restore-dump.sh", target_path])
