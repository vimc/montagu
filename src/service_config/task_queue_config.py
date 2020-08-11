import yaml
import paths
from os.path import join
from docker_helpers import docker_cp, docker_cp_from


def configure_task_queue(service):
    container = service.task_queue

    print("Configuring Task Queue")

    print("- reading config from container")
    local_config_file = join(paths.config, "task_queue_config.yml")
    container_config_file = "home/worker/config/config.yml"
    docker_cp_from(container.name, container_config_file, local_config_file)
    with open(local_config_file, "r") as ymlfile:
        config = yaml.load(ymlfile, Loader=yaml.FullLoader)
    print("loaded config:" + str(config))

