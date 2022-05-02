from string import Template
import string
import requests


def get_latest_release_info(owner: string, repo: string):
    api_template = Template(
        "https://api.github.com/repos/${owner}/${repo}/releases/latest")
    api_address = api_template.substitute(owner=owner, repo=repo)
    return _get(api_address)


# api: https://api.github.com/repos/:owner/:repo/commits?path=:file_path
def get_file_commit_info(owner: string, repo: string, file_path: string):
    api_template = Template(
        "https://api.github.com/repos/${owner}/${repo}/commits?path=${repo}")
    api_address = api_template.substitute(
        owner=owner, repo=repo, file_path=file_path)
    return _get(api_address)


def _get(api: string):
    return requests.get(api).json()
