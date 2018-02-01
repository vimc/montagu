from os.path import join

from docker_helpers import copy_between_volumes


def configure_contrib_portal(service):
    template_report_paths = get_template_report_versions()
    print("Configuring contrib portal")
    for p in template_report_paths:
        if len(p) > 0:
            path_to_templates = join("archive", p, "*.csv")
            add_templates_to_contrib_portal(service, path_to_templates)


def add_templates_to_contrib_portal(service, path_to_templates):
    print("- Copying burden estimate templates from orderly to contrib portal")
    copy_between_volumes(service.volume_name("orderly"),
                         service.volume_name("templates"), path_to_templates)


def get_template_report_versions():
    with open("template_report_versions") as f:
        value = f.read()
    return [x.strip() for x in value.split("\n") if x]
