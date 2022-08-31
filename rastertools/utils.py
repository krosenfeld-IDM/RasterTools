#!/usr/bin/env python

import hashlib
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

def extract_archive(file_path: Union[str, Path]):
    dst_dir = file_path.parent.joinpath(file_path.stem)
    Path(dst_dir).mkdir(exist_ok=True, parents=True)
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        print(f"Extracting file {file_path}")
        zip_ref.extractall(dst_dir)

    extracted_files = [str(f) for f in Path(dst_dir).rglob("*.*")]
    return extracted_files


def sha256(file_path):
    # https://www.quickprogrammingtips.com/python/how-to-calculate-sha256-hash-of-a-file-in-python.html
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()
