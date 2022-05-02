import string
from textwrap import indent
import requests
import json
import toml
from string import Template
import github

owner = "acidanthera"
repo = "OpenCorePkg"


def parse_package_config():
    parsed_config = toml.load("packages.toml")
    pass

def pretty_json(origin_data):
    print(json.dumps(origin_data, indent=2))

# release_info = github.get_latest_release_info(owner, repo)
# print(json.dumps(release_info, indent=2))
# version = release_info["name"]
# print(version)


parse_package_config()
