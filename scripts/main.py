import logging
import json
import os.path
from open_core import OpenCore
from constant import ROOT_DIR

logging.basicConfig(level=logging.INFO)


def pretty_json(origin_data):
    print(json.dumps(origin_data, indent=2))


opencore = OpenCore(os.path.join(ROOT_DIR, "packages.toml"))
opencore.update()
