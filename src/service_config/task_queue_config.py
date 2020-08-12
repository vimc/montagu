import yaml
import paths
from os.path import join
from docker_helpers import docker_cp, docker_cp_from


def configure_task_queue(service, hostname, montagu_user, orderly_web_url, is_prod):
    container = service.task_queue

    print("Configuring Task Queue")

    print("- reading config from container")
    local_config_file = join(paths.config, "task_queue_config.yml")
    container_config_file = "home/worker/config/config.yml"
    docker_cp_from(container.name, container_config_file, local_config_file)
    with open(local_config_file, "r") as ymlfile:
        config = yaml.load(ymlfile, Loader=yaml.FullLoader)

    print("- adding settings to config")
    montagu = config["servers"]["montagu"]
    montagu["url"] = "https://{}/api".format(hostname)
    if montagu_user is not None:
        montagu["user"] = montagu_user
        # TODO: password

    # Task queue needs orderly-web url without /api/v1 suffix
    ow_url_trimmed = orderly_web_url.replace("/api/v1", "")
    config["servers"]["orderlyweb"]["url"] = ow_url_trimmed

    if is_prod:
        smtp = config["servers"]["smtp"]
        smtp["host"] = "smtp.cc.ic.ac.uk"
        smtp["port"] = 587
        smtp["from"] = "montagu.notifications@imperial.ac.uk"

    print("- writing config to container:")
    print(str(config))
    with open(local_config_file, "w") as file:
        yaml.dump(config, file)
    docker_cp(local_config_file, container.name, container_config_file)



