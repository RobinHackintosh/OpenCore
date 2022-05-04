import json
import os.path
from open_core import OpenCore
from constant import ROOT_DIR


def pretty_json(origin_data):
    print(json.dumps(origin_data, indent=2))


opencore = OpenCore(os.path.join(ROOT_DIR, "packages.toml"))
need_update, remote_publish_date, assets = opencore.check_opencore()
if need_update:
    opencore.update_opencore(remote_publish_date, assets)
