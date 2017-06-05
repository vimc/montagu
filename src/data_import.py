from subprocess import check_output

from service import service
from teamcity import save_artifact


def do(settings):
    source = settings["initial_data_source"]
    print("Running initial data import with mode: {}".format(source))
    if source == "none":
        print("- Nothing to do")
    elif source == "minimal":
        import_sql("../initial_data/minimal.sql")
    elif source == "test_data":
        import_sql("../initial_data/test.sql")
    elif source == "legacy":
        import_artifact("montagu_MontaguLegacyData_Build", "montagu.dump", "legacy-data.dump")
    else:
        raise Exception("Unknown mode '{}'".format(source))


def import_sql(sql_path):
    print("- Copying {} to DB container and importing into database".format(sql_path))
    target_path = "/tmp/import.sql"
    full_target = "{container}:{path}".format(container=service.db.name, path=target_path)
    check_output(["docker", "cp", sql_path, full_target])
    check_output(["docker", "exec", service.db.name, "psql", "-U", "vimc", "-d", "montagu", "-f", target_path])


def import_dump(dump_path):
    print("- Copying {} to DB container and importing into database".format(dump_path))
    target_path = "/tmp/import.dump"
    full_target = "{container}:{path}".format(container=service.db.name, path=target_path)
    check_output(["docker", "cp", dump_path, full_target])
    check_output(["docker", "exec", service.db.name, "/montagu-bin/restore-dump.sh", target_path])


def import_artifact(build_type, remote_path, local_name):
    print("- Downloading {remote_path} from TeamCity (build type ID: {build_type} and saving as {local_name}".format(
        remote_path=remote_path, build_type=build_type, local_name=local_name))
    local_path = save_artifact(build_type, remote_path, local_name)
    import_dump(local_path)
