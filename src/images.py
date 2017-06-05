registry_url = "montagu.dide.ic.ac.uk:5000"


def get_image_name(name, version):
    return "{url}/{name}:{version}".format(url=registry_url, name=name, version=version)
