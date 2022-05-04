from string import Template
import string
import requests
from datetime import datetime


def get_latest_release_info(owner: string, repo: string):
    api_template = Template(
        "https://api.github.com/repos/${owner}/${repo}/releases/latest")
    api_address = api_template.substitute(owner=owner, repo=repo)
    return _get(api_address)


def has_new_release(local_publish_date, owner: string, repo: string) -> (bool, str, dict):
    release_info = get_latest_release_info(owner, repo)
    remote_publish_date = release_info["published_at"]
    assets = release_info["assets"]

    if type(local_publish_date) == int:
        print("local machine has no record about ")
        return True, remote_publish_date, assets
    else:
        has_new_version = datetime.strptime(remote_publish_date,
                                            "%Y-%m-%dT%H:%M:%SZ").timestamp() > local_publish_date.timestamp()
        return has_new_version, remote_publish_date, assets


# api: https://api.github.com/repos/:owner/:repo/commits?path=:file_path
def get_file_commit_info(owner: string, repo: string, file_path: string):
    api_template = Template(
        "https://api.github.com/repos/${owner}/${repo}/commits?path=${repo}")
    api_address = api_template.substitute(
        owner=owner, repo=repo, file_path=file_path)
    return _get(api_address)


def _get(api: string):
    return requests.get(api).json()
