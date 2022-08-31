# Workflow for downloading rasters and shapefiles from GDx for local processing.

import os
import requests
import zipfile

from appdirs import user_cache_dir
from ckanapi import RemoteCKAN
from pathlib import Path
from requests import Response
from typing import Union, Dict

from rastertools.utils import read_json, save_json, extract_archive, sha256


def get_remote(key_file=None) -> RemoteCKAN:
    """Authentication; expects GDx API token in GDX.id; DON'T PUT GDX.id IN REPO"""
    if key_file is not None and Path(key_file).is_file():
        apikey = Path(key_file).read_text().strip()
    else:
        apikey = os.getenv('CKAN_API_KEY').rstrip('\n')

    if apikey is None:
        raise ValueError("Unable to read GDX API key")

    return RemoteCKAN('https://dataexchange.gatesfoundation.org', apikey=apikey)


def download(data_id: str,
             data_dir: str = "datasets",
             dataset: bool = False,
             prefix=None,
             suffix=None,
             create_subdir=False,
             force: bool = False,
             extract: bool = False,
             remote: RemoteCKAN = None) -> Response:
    """Resource identification; string table below for convenience"""
    remote = remote or get_remote()

    if dataset:
        dst = get_metadata(remote, id=data_id)
        if create_subdir:
            data_dir = Path(data_dir).joinpath(dst['name'])
        resource_ids = [r['id'] for r in dst['resources']]
    else:
        resource_ids = [data_id]

    files = []
    for rid in resource_ids:
        meta = get_metadata(remote, entity_id=rid, is_package=False)
        file_path = get_file_path(meta, data_dir, prefix, suffix)
        if file_path is None:
            print(f"Skipping {file_path} because of prefix/suffix filter.")
            continue

        has_file = file_path.is_file() and sha256(file_path) == meta["sha256"]
        if force or not has_file:    # TODO: also consider file hash
            print(f"Downloading {file_path}.")
            _download_url_to_file(remote, meta['url'], file_path)
        else:
            print(f"Skipping {file_path} because file already exists. Use force flag to override.")

        if extract and file_path.suffix == ".zip":
            extracted_files = extract_archive(file_path)
            files.extend(extracted_files)
        else:
            files.append(str(file_path))

    if len(files) == 1:
        files = files[0]

    return files


def _get_cache_path( entity_id: str, is_package: bool):
    cache_dir = Path(user_cache_dir("rastertools"))
    cache_dir.mkdir(exist_ok=True)
    entity_type = "package" if is_package else "resource"
    return cache_dir.joinpath(entity_type).joinpath(f"{entity_id}.json")


def get_metadata(remote: RemoteCKAN, entity_id: str, is_package: bool = True) -> Dict:
    try:
        show_action = remote.action.package_show if is_package else remote.action.resource_show
        meta = show_action(id=entity_id)
        save_json(meta, json_path=_get_cache_path(entity_id, is_package))
    except requests.exceptions.ConnectionError as ex:
        meta_path = _get_cache_path(entity_id, is_package)
        meta = read_json(meta_path) if meta_path.is_file() else None
    return meta


def _download_url_to_file(remote: RemoteCKAN, url: str, file_path: Union[str, Path]):
    file_obj = requests.get(url=url,
                            headers={'Authorization': remote.apikey},
                            allow_redirects=True,
                            params={'sensitive': 'true'})
    # Save file locally
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(str(file_path), 'wb') as fid01:
        fid01.write(file_obj.content)

    return file_path


def get_file_path(meta:Dict, data_dir: Union[str, Path], prefix: str, suffix: str):
    file_name = meta['name']
    if "." not in file_name:
        file_name = f"{file_name}.{meta['format']}".lower()

    file_path = Path(data_dir).joinpath(file_name)

    prefix_ok = prefix is None or file_name.startswith(prefix)
    suffix_ok = suffix is None or file_name.endswith(suffix)
    return file_path if prefix_ok and suffix_ok else None


