from string import Template
import string
import requests
from datetime import datetime


def get_latest_release_info(owner: string, repo: string):
    api_template = Template(
        "https://api.github.com/repos/${owner}/${repo}/releases/latest")
    api_address = api_template.substitute(owner=owner, repo=repo)
    return _get(api_address)


def has_new_release(local_publish_date, owner: str, repo: str) -> (bool, str, dict):
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
def get_file_commit_history(owner: str, repo: str, file_path: str):
    api_address = f"https://api.github.com/repos/{owner}/{repo}/commits?path={file_path}"
    print(api_address)
    return _get(api_address)


def has_new_commit(owner: str, repo: str, file_path: str, commit_date: datetime) -> (bool, datetime):
    commit_history = get_file_commit_history(owner, repo, file_path)
    latest_commit_info = commit_history[0]
    latest_commit_date = datetime.strptime(latest_commit_info["commit"]["committer"]["date"],
                                           "%Y-%m-%dT%H:%M:%SZ")
    should_update = latest_commit_date.timestamp() > commit_date.timestamp()
    return should_update, latest_commit_date


def _get(api: string):
    return requests.get(api).json()
