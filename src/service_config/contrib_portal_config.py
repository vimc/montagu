from docker_helpers import copy_between_volumes
from os.path import join


def configure_contrib_portal(service):
    guidance_paths = get_report_versions("guidance_report_versions")
    print("Configuring contrib portal")
    for p in guidance_paths:
        if len(p) > 0:
            path_to_artefacts = join("archive", p, "*.html")
            add_reports_to_contrib_portal(service, path_to_artefacts, "guidance")


def add_reports_to_contrib_portal(service, path_to_reports, volume_name):
    print("- Copying {} reports from orderly to contrib portal".format(volume_name))
    copy_between_volumes(service.volume_name("orderly"), service.volume_name(volume_name), path_to_reports)


def get_report_versions(path):
    with open(path) as f:
        value = f.read()
    return [x.strip() for x in value.split("\n") if x]

