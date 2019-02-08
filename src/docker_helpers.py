from subprocess import check_output, run
import os

montagu_registry_local = "docker.montagu.dide.ic.ac.uk:5000"
montagu_registry_hub = "vimc"

# This is really ugly, but the alternative is to alter every call to
# get_image_name and that feels much more invasive right now.
try:
    use_docker_hub = os.environ['MONTAGU_USE_DOCKER_HUB'] == "true"
except KeyError:
    use_docker_hub = False

montagu_registry = montagu_registry_hub if use_docker_hub else montagu_registry_local


def get_image_name(name, version):
    return "{url}/{name}:{version}".format(url=montagu_registry, name=name, version=version)


def docker_cp(src, container, target_path):
    full_target = "{container}:{path}".format(container=container, path=target_path)
    check_output(["docker", "cp", src, full_target])


def pull(image):
    run(["docker", "pull", image], check=True)


def copy_between_volumes(source_volume, destination_volume, path_to_copy, destination_path="."):
    run(["docker", "run", "--rm", "-i", "-t",
         "-v", "{}:/from".format(source_volume),
         "-v", "{}:/to".format(destination_volume),
         "alpine",
         "ash",
         "-c",
         "cd /to ; mkdir -p {} && find /from/{} -exec cp -a {{}} {} \;".format(destination_path, path_to_copy,
                                                                               destination_path)
         ], check=True)


# Somewhat surprisingly, the `container.exec_run` method does not
# support a `check=True` like option, nor does it let you inspect
# anything about the process that was run except for the outoput.  The
# lower-level docker api supports getting this information though.
#
#     exec_safely(container, cmd)
#
# is roughly equivalent to
#
#     container.exec_run(cmd)
#
# except the return value is a dict (with output as the element
# 'Output').  If `check=True`, then if the command returns a nonzero
# exit code then raise a python exception.
#
# This will be fixed docker python sdk (> 3.0.0), which will also
# break backward compatibility with exec_run
#
#     https://github.com/docker/docker-py/pull/1797
#     https://github.com/docker/docker-py/releases/tag/3.0.0
def exec_safely(container, cmd, check=False):
    api = container.client.api
    exec_id = api.exec_create(container.id, cmd)['Id']
    out = api.exec_start(exec_id)
    dat = api.exec_inspect(exec_id)
    dat['Output'] = out
    if check and dat['ExitCode'] != 0:
        msg = out.decode("UTF-8").strip()
        raise Exception("Exec failed with message '{}'".format(msg))
    return dat
