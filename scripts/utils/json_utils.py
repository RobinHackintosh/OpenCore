import json


def pretty_json(origin_data):
    print(json.dumps(origin_data, indent=2))
