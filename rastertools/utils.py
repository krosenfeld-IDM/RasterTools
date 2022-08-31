"""
Helper functions used by other package modules.

"""

import hashlib
import json
import re
import requests
import zipfile

from pathlib import Path
from typing import Any, Callable, Dict, List, Union


def read_json(json_path: str) -> Dict[str, Any]:
    """
    Read a json file.
    :param json_path: Json file path.
    :return: A dictionary representing json structure.
    """
    assert Path(json_path).exists(), f"JSON file {json_path} not found."
    with open(json_path) as fp:
        data: Dict = json.load(fp)

    return data


def save_json(data: Dict, json_path, sort_keys=False, indent=4) -> None:
    """
    Saving json object into a file.
    :param data: Json object.
    :param json_path: Json file path.
    :param sort_keys: Flag indicating whether to sort json by key.
    :param indent: Ident to use when pretty-formatting json file.
    :return:
    """
    Path(json_path).parent.mkdir(exist_ok=True)
    with open(json_path, 'w') as fp:
        json.dump(data, fp, sort_keys=sort_keys, indent=indent)


def extract_archive(file_path: Union[str, Path]) -> List[str]:
    """
    Extract a zip archive into a dir with the same name (as file's base name).
    :param file_path: A zip file path.
    :return: List of extracted file paths.
    """
    dst_dir = file_path.parent.joinpath(file_path.stem)
    Path(dst_dir).mkdir(exist_ok=True, parents=True)
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        print(f"Extracting file {file_path}")
        zip_ref.extractall(dst_dir)

    extracted_files = [str(f) for f in Path(dst_dir).rglob("*.*")]
    return extracted_files


def sha256(file_path) -> str:
    """
    https://www.quickprogrammingtips.com/python/how-to-calculate-sha256-hash-of-a-file-in-python.html
    :param file_path:
    :return: A string representing sha256 hash hex digest.
    """
    if not Path(file_path).is_file():
        return ""

    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()
