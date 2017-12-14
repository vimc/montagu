from service import orderly_volume_name, template_volume_name
from docker_helpers import copy_between_volumes


def configure_contrib_portal(template_report_version):
    print("Configuring contrib portal")
    path_to_templates = "archive/internal-2017-burden-estimates-template/{}/*.csv".format(template_report_version)
    add_templates_to_contrib_portal(path_to_templates)


def add_templates_to_contrib_portal(path_to_templates):
    print("- Copying burden estimate templates from orderly to contrib portal")
    copy_between_volumes(orderly_volume_name, template_volume_name, path_to_templates)

