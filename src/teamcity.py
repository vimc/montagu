from getpass import getpass
from os import makedirs

import requests
from requests.auth import HTTPBasicAuth


class AuthProvider:
    def __init__(self):
        self.auth = None

    def get(self):
        if self.auth is None:
            print("- Please enter your TeamCity credentials:")
            username = input("  - Username: ")
            password = getpass("  - Password: ")
            self.auth = HTTPBasicAuth(username, password)
        return self.auth


def get_artifact(build_type: str, artifact_path: str):
    template = "{root_url}/app/rest/builds/buildType:(id:{build_type}),status:SUCCESS/artifacts/content/{artifact_path}"
    url = template.format(root_url=teamcity_url, build_type=build_type, artifact_path=artifact_path)
    r = requests.get(url, auth=auth.get())
    if r.status_code != 200:
        raise Exception("Failed to retrieve artifact from TeamCity using url {url}\n".format(url=url) +
                        "Returned status code {code}.\n".format(code=r.status_code) +
                        "Full response text: " + r.text)
    return r.content


def save_artifact(build_type: str, artifact_path: str, name: str):
    makedirs('../artifacts', exist_ok=True)
    local_path = '../artifacts/' + name
    with open(local_path, 'wb') as f:
        data = get_artifact(build_type, artifact_path)
        f.write(data)
    return local_path


teamcity_url = "http://montagu.dide.ic.ac.uk:8111"
auth = AuthProvider()
