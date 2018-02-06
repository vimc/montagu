from docker_helpers import copy_between_volumes
from os.path import join


def configure_contrib_portal(service):
    template_report_paths = get_template_report_versions()
    guidance_paths = get_guidance_report_versions()
    print("Configuring contrib portal")
    for p in template_report_paths:
        if len(p) > 0:
            path_to_templates = join("archive", p, "*.csv")
            add_templates_to_contrib_portal(service, path_to_templates)
    for p in guidance_paths:
        if len(p) > 0:
            path_to_artefacts = join("archive", p, "*.csv")
            add_guidance_to_contrib_portal(service, path_to_artefacts)


def add_templates_to_contrib_portal(service, path_to_templates):
    print("- Copying burden estimate templates from orderly to contrib portal")
    copy_between_volumes(service.volume_name("orderly"), service.volume_name("templates"), path_to_templates)


def add_guidance_to_contrib_portal(service, path_to_reports):
    print("- Copying burden estimate templates from orderly to contrib portal")
    copy_between_volumes(service.volume_name("orderly"), service.volume_name("guidance"), path_to_reports)


def get_template_report_versions():
    with open("template_report_versions") as f:
        value = f.read()
    return [x.strip() for x in value.split("\n") if x]


def get_guidance_report_versions():
    with open("guidance_report_versions") as f:
        value = f.read()
    return [x.strip() for x in value.split("\n") if x]
