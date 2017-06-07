from subprocess import check_output

registry_url = "montagu.dide.ic.ac.uk:5000"


def get_image_name(name, version):
    return "{url}/{name}:{version}".format(url=registry_url, name=name, version=version)


def docker_cp(src, container, target_path):
    full_target = "{container}:{path}".format(container=container, path=target_path)
    check_output(["docker", "cp", src, full_target])
