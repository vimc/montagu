from subprocess import check_output

import backup
import versions
from docker_helpers import docker_cp
from teamcity import save_artifact


def do(service):
    source = service.settings["initial_data_source"]
    print("Running initial data import with mode: {}".format(source))
    if source == "minimal":
        print("- Nothing to do (migrations will insert minimal data)")
    elif source == "test_data":
        local_path = get_artifact("montagu_api_generate_test_data", "test-data.bin", commit_hash=versions.api)
        import_dump(service.db, local_path)
    elif source == "legacy":
        local_path = get_artifact("montagu_MontaguLegacyData_Build", "montagu.dump", "legacy-data.dump")
        import_dump(service.db, local_path)
    elif source == "restore":
        backup.restore(service)
    else:
        raise Exception("Unknown mode '{}'".format(source))


# def import_sql(db, sql_path):
#     print("- Copying {} to DB container and importing into database".format(sql_path))
#     target_path = "/tmp/import.sql"
#     docker_cp(sql_path, db.name, target_path)
#     check_output(["docker", "exec", db.name, "psql", "-U", "vimc", "-d", "montagu", "-f", target_path])


def import_dump(db, dump_path):
    print("- Copying {} to DB container and importing into database".format(dump_path))
    target_path = "/tmp/import.dump"
    docker_cp(dump_path, db.name, target_path)
    check_output(["docker", "exec", db.name, "/montagu-bin/restore-dump.sh", target_path])


def get_artifact(build_type, remote_path, local_name=None, commit_hash=None):
    local_name = local_name or remote_path
    print("- Downloading {remote_path} from TeamCity (build type ID: {build_type}) and saving as {local_name}".format(
        remote_path=remote_path, build_type=build_type, local_name=local_name))
    return save_artifact(build_type, remote_path, local_name, commit_hash)
