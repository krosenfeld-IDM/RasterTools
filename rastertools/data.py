# Workflow for downloading rasters and shapefiles from GDx for local processing.

import os
import requests
import zipfile

from ckanapi import RemoteCKAN
from pathlib import Path
from requests import Response


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
        dst = remote.action.package_show(id=data_id)
        if create_subdir:
            data_dir = Path(data_dir).joinpath(dst['name'])
        resource_ids = [r['id'] for r in dst['resources']]
    else:
        resource_ids = [data_id]

    files = []
    for rid in resource_ids:
        rsc = remote.action.resource_show(id=rid)
        file_name = rsc['name']
        if "." not in file_name:
            file_name = f"{file_name}.{rsc['format']}".lower()

        file_path = Path(data_dir).joinpath(file_name)

        prefix_filter_out = prefix is not None and not file_name.startswith(prefix)
        suffix_filter_out = suffix is not None and not file_name.endswith(suffix)
        if prefix_filter_out or suffix_filter_out:
            print(f"Skipping {file_path} because of prefix/suffix filter.")
            continue

        if force or not file_path.is_file():    # TODO: also consider file hash
            print(f"Downloading {file_path}.")
            file_obj = requests.get(url=rsc['url'],
                                    headers={'Authorization': remote.apikey},
                                    allow_redirects=True,
                                    params={'sensitive': 'true'})
            # Save file locally
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(str(file_path), 'wb') as fid01:
                fid01.write(file_obj.content)
        else:
            print(f"Skipping {file_path} because file already exists. Use force flag to override.")

        if extract and file_path.suffix == ".zip":
            dst_dir = file_path.parent.joinpath(file_path.stem)
            Path(dst_dir).mkdir(exist_ok=True, parents=True)
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                print(f"Extracting file {file_path}")
                zip_ref.extractall(dst_dir)

            extracted_files = [str(f) for f in Path(dst_dir).rglob("*.*")]
            files.extend(extracted_files)
        else:
            files.append(str(file_path))

    if len(files) == 1:
        files = files[0]

    return files

