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


def save_json(data: Dict, json_path):
    Path(json_path).parent.mkdir(exist_ok=True)
    with open(json_path, 'w') as fp:
        json.dump(data, fp, indent=4)


def download(url, path: Union[Path, str], extract=False, force=False) -> str:
    path = Path(path)
    if path.is_dir() or path.suffix == "":
        file_path = path.joinpath(Path(url).name)
    else:
        file_path = path

    if force or not file_path.is_file():
        file_path.parent.mkdir(parents=True, exist_ok=True)
        resp = requests.get(url)
        assert resp.status_code == 200, "Request failed"
        with open(str(file_path), "wb") as f:
            f.write(resp.content)

    if extract and file_path.suffix == ".zip":
        with zipfile.ZipFile(str(file_path), 'r') as zip_ref:
            zip_ref.extractall(str(file_path.parent))

    return str(file_path)


# def files_meta_dict(files: List[str], pattern: str) -> Dict:
#     return {}

