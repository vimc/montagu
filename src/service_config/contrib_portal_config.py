from service import orderly_volume_name, template_volume_name
from docker_helpers import copy_between_volumes
from os.path import join


def configure_contrib_portal(template_report_paths):
    print("Configuring contrib portal")
    for p in template_report_paths:
        if len(p) > 0:
            path_to_templates = join("archive", p, "*.csv")
            add_templates_to_contrib_portal(path_to_templates)


def add_templates_to_contrib_portal(path_to_templates):
    print("- Copying burden estimate templates from orderly to contrib portal")
    copy_between_volumes(orderly_volume_name, template_volume_name, path_to_templates)

