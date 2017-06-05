from subprocess import check_output

from service import service


def do(settings):
    source = settings["initial_data_source"]
    print("Running initial data import with mode: {}".format(source))
    if source == "none":
        print("Nothing to do")
    elif source == "minimal":
        import_dump("../initial_data/minimal.sql")
    elif source == "test_data":
        import_dump("../initial_data/test.sql")
    else:
        raise Exception("Unknown mode '{}'".format(source))


def import_dump(sql_path):
    print("- Copying {} to DB container and importing into database".format(sql_path))
    target_path = "/tmp/import.sql"
    full_target = "{container}:{path}".format(container=service.db.name, path=target_path)
    check_output(["docker", "cp", sql_path, full_target])
    check_output(["docker", "exec", service.db.name, "psql", "-U", "vimc", "-d", "montagu", "-f", target_path])
