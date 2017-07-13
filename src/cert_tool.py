from os.path import abspath
from subprocess import PIPE, run

import versions
from docker_helpers import get_image_name


def run_cert_tool(mode, volume_path, args=[], stdout=PIPE):
    image = get_image_name("montagu-cert-tool", versions.cert_tool)
    volume = "{}:{}".format(abspath(volume_path), "/working")
    command = ["docker", "run", "--rm", "-v", volume, image, mode]
    run(command + args, stdout=stdout, stderr=PIPE)
