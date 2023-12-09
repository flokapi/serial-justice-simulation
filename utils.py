from pathlib import Path
import json


def get_abi(_file_path):
    contract_abi = Path(f"env/abi/{_file_path}").read_text()
    return json.loads(contract_abi)["abi"]


def get_json(path):
    text = Path(path).read_text()
    return json.loads(text)


def get_private_keys():
    return get_json("env/private_keys.json")


def get_config():
    return get_json("env/config.json")
