import yaml
import paths
from os.path import join
from docker_helpers import docker_cp, docker_cp_from
from settings import get_secret


def configure_task_queue(service, montagu_email, montagu_password,
                         orderly_web_url, use_real_diagnostic_reports,  fake_smtp):
    container = service.task_queue

    print("Configuring Task Queue")
    print("- reading config from container")
    local_config_file = join(paths.config, "task_queue_config.yml")
    container_config_file = "home/worker/config/config.yml"
    docker_cp_from(container.name, container_config_file, local_config_file)
    with open(local_config_file, "r") as ymlfile:
        config = yaml.load(ymlfile, Loader=yaml.FullLoader)

    print("- reading diagnostic reports")
    reports_cfg_filename = "real_diagnostic_reports.yml" if use_real_diagnostic_reports else "test_diagnostic_reports.yml"
    local_reports_cfg_file = join(paths.container_config, "task_queue", reports_cfg_filename)
    with open(local_reports_cfg_file, "r") as ymlfile:
        diag_reports = yaml.load(ymlfile, Loader=yaml.FullLoader)

    print("- adding settings to config")
    montagu = config["servers"]["montagu"]
    montagu["url"] = "http://montagu_api_1:8080"
    montagu["user"] = montagu_email
    montagu["password"] = montagu_password

    # Task queue needs orderly-web url without /api/v1 suffix
    ow_url_trimmed = orderly_web_url.replace("/api/v1", "")
    config["servers"]["orderlyweb"]["url"] = ow_url_trimmed

    config["tasks"]["diagnostic_reports"]["reports"] = diag_reports

    smtp = config["servers"]["smtp"]
    smtp["from"] = "montagu-help@imperial.ac.uk"
    if fake_smtp:
        smtp["host"] = "montagu_fake_smtp_server_1"
    else:
        smtp["host"] = "smtp.cc.ic.ac.uk"
        smtp["port"] = 587
        smtp["user"] = "montagu"
        smtp["password"] = get_secret("email/password")

    print("- writing config to container")
    with open(local_config_file, "w") as file:
        yaml.dump(config, file)
    docker_cp(local_config_file, container.name, container_config_file)
