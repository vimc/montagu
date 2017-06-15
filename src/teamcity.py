from getpass import getpass
from os import makedirs
from os.path import join
from xml.etree import ElementTree

import requests
from requests.auth import HTTPBasicAuth

import paths


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


def get_safely(url, as_text=True):
    r = requests.get(url, auth=auth.get())
    if r.status_code != 200:
        raise Exception("Failed to retrieve artifact from TeamCity using url {url}\n".format(url=url) +
                        "Returned status code {code}.\n".format(code=r.status_code) +
                        "Full response text: " + r.text)
    if as_text:
        return r.text
    else:
        return r.content


def save_artifact(build_type: str, artifact_path: str, name: str, commit_hash=None):
    makedirs(paths.artifacts, exist_ok=True)
    local_path = join(paths.artifacts, name)
    with open(local_path, 'wb') as f:
        if commit_hash:
            data = get_artifact(build_type, artifact_path, commit_hash)
        else:
            data = get_latest_artifact(build_type, artifact_path)
        f.write(data)
    return local_path


def get_latest_artifact(build_type, artifact_path):
    template = "{root_url}/builds/buildType:(id:{build_type}),status:SUCCESS"
    build_url = template.format(root_url=teamcity_api_url, build_type=build_type)
    return download_artifact(build_url, artifact_path)


def get_artifact(build_type, artifact_path, commit_hash):
    fields = "build(id,href,revisions(revision))"
    locator = "buildType:(id:{build_type}),status:SUCCESS".format(build_type=build_type)
    template = "{root_url}/builds/?locator={locator}&fields={fields}"
    url = template.format(root_url=teamcity_api_url, locator=locator, fields=fields)
    xml = get_safely(url)
    build_url = find_url_of_matching_build(xml, commit_hash)
    if build_url is None:
        raise Exception("Unable to find build of type '{build_type}' with commit hash '{hash}'"
                        .format(build_type=build_type, hash=commit_hash))
    build_url = teamcity_url + build_url
    return download_artifact(build_url, artifact_path)


def download_artifact(build_url, artifact_path):
    template = "{build_url}/artifacts/content/{artifact_path}"
    url = template.format(build_url=build_url, artifact_path=artifact_path)
    return get_safely(url, as_text=False)


def find_url_of_matching_build(xml_text, commit_hash):
    xml = ElementTree.fromstring(xml_text)
    for build in xml.findall('build'):
        revisions = build.find('revisions').findall('revision')
        hashes = set(r.get('version') for r in revisions)
        if any(h for h in hashes if h.startswith(commit_hash)):
            return build.get("href")
    return None


teamcity_url = "http://teamcity.montagu.dide.ic.ac.uk:8111"
teamcity_api_url = teamcity_url + "/app/rest"
auth = AuthProvider()
