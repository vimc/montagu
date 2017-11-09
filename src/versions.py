import re
from os.path import join
from subprocess import run, PIPE


def get_submodule_version(path):
    full_path = join("submodules", path)
    result = run(["git", "submodule", "status", full_path], stdout=PIPE, check=True, universal_newlines=True)
    text = result.stdout
    if text[0] in [" ", "+", "-"]:
        parts = text[1:].split(" ")
        commit_hash = parts[0]
        if re.match(r"[0-9a-f]{40}", commit_hash):
            version = commit_hash[:7]
            return version
    raise Exception("Unable to understand Git status for submodule '{}': {}".format(path, text))


db = get_submodule_version("db")
orderly = get_submodule_version("orderly")

api = get_submodule_version("api")
reporting_api = get_submodule_version("reporting-api")

contrib_portal = get_submodule_version("contrib-portal")
admin_portal = get_submodule_version("admin-portal")
report_portal = get_submodule_version("report-portal")

proxy = get_submodule_version("proxy")
cert_tool = get_submodule_version("cert-tool")


def as_dict():
    return {
        'db': db,
        'orderly': orderly,
        'api': api,
        'reporting_api': api,
        'contrib_portal': contrib_portal,
        'admin_portal': admin_portal,
        'report_portal': report_portal,
        'proxy': proxy,
        'cert_tool': cert_tool
    }
