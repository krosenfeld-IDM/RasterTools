#!/usr/bin/env python

import json
import re
import requests
import zipfile

from pathlib import Path
from typing import Callable, Dict, List, Union


def read_json(json_path: str):
    assert Path(json_path).exists(), f"JSON file {json_path} not found."
    with open(json_path) as fp:
        data: Dict = json.load(fp)

    return data


def save_json(data: Dict, json_path, sort_keys=False, indent=4):
    Path(json_path).parent.mkdir(exist_ok=True)
    with open(json_path, 'w') as fp:
        json.dump(data, fp, sort_keys=sort_keys, indent=indent)


# def files_meta_dict(files: List[str], pattern: str) -> Dict:
#     return {}

