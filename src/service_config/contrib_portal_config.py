from docker_helpers import copy_between_volumes
from os.path import join


def configure_contrib_portal(service, template_report_paths):
    print("Configuring contrib portal")
    for p in template_report_paths:
        if len(p) > 0:
            path_to_templates = join("archive", p, "*.csv")
            add_templates_to_contrib_portal(service, path_to_templates)


def add_templates_to_contrib_portal(service, path_to_templates):
    print("- Copying burden estimate templates from orderly to contrib portal")
    copy_between_volumes(service.volume_name("orderly"), service.volume_name("templates"), path_to_templates)

