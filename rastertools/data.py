"""
Functions for downloading raster and shapefiles from GDx to a local dir. Supports local caching so that data is
downloaded only when it doesn't exist locally or if it was modified on the GDx side. Also, supports offline mode,
meaning after data has been downloaded once access to GDx is no longer needed for scripts to work.
"""

import os
import requests
import zipfile

from appdirs import user_cache_dir
from ckanapi import RemoteCKAN
from pathlib import Path
from typing import Dict, List, Union

from rastertools.utils import read_json, save_json, extract_archive, sha256


def get_remote(key_file: Union[str, Path] = None) -> RemoteCKAN:
    """
    Authentication; expects GDx API token in GDX.id; DON'T PUT GDX.id IN REPO
    :param key_file: A file cDx API token.
    :return: RemoteCKAN object, used to access datasets.
    """
    if key_file is not None and Path(key_file).is_file():   # If key file is specified and exists.
        apikey = Path(key_file).read_text().strip()         # Read API token from the file.
    else:
        apikey = os.getenv('CKAN_API_KEY').rstrip('\n')     # Otherwise, read it from the CKAN environment variable.

    if apikey is None:
        raise ValueError("Unable to read GDX API key")

    return RemoteCKAN('https://dataexchange.gatesfoundation.org', apikey=apikey, get_only=True) # Init read-only remote.


def download(data_id: str,
             data_dir: str = "datasets",
             is_dataset: bool = False,
             prefix: str = None,
             suffix: str = None,
             create_subdir: bool = False,
             force: bool = False,
             extract: bool = False,
             remote: RemoteCKAN = None) -> Union[List[str], str]:
    """
    Resource identification; string table below for convenience.
    :param data_id: GDx dataset id (guid).
    :param data_dir: A local dir where downloaded data is stored.
    :param is_dataset: A flag indicating if data consists of a number of resources or a single resource.
    :param prefix: Prefix used to filter resources by name prefix.
    :param suffix: Suffix used to filter resources by name suffix.
    :param create_subdir: If set, a sub dir is created to store dataset files.
    :param force: Force download even if resources already exists and have not changed.
    :param extract: Whether to extract resources which are zip archives.
    :param remote: A CKAN remote to be used (instead of instantiating a new remote object).
    :return: List of downloaded files or a single downloaded file.
    """
    remote = remote or get_remote()

    if is_dataset:                                      # If ID is a dataset (with multiple resources),
        dst = get_metadata(remote, entity_id=data_id)          # get its metadata (containing a list of resources).
        if create_subdir:
            data_dir = Path(data_dir).joinpath(dst['name'])
        resource_ids = [r['id'] for r in dst['resources']]  # Create a list of all the resources to be downloaded.
    else:
        resource_ids = [data_id]                        # If ID is a single resource, create a single element list.

    files = []
    for rid in resource_ids:                            # For each specified resource run the download code sequence.
        meta = get_metadata(remote, entity_id=rid, is_dataset=False)         # Get resource metadata (containing url).
        file_path = get_file_path(meta, data_dir, prefix, suffix)            # Construct file path (from metadata).
        if file_path is None:                                                # If None, name is filtered out and
            print(f"Skipping {file_path} because of prefix/suffix filter.")  # the file download is skipped.
            continue                                                         # So, move to the next resource.

        no_file = not file_path.is_file()                           # Is file missing
        is_diff = sha256(file_path) != meta["sha256"]               # Is file different (hash not matching GDx metadata)
        if force or no_file or is_diff:                             # Determine if file download is needed.
            print(f"Downloading {file_path}.")
            _download_url_to_file(remote, meta['url'], file_path)   # Download based on url from metadata
        else:
            print(f"Skipping {file_path} because file already exists. Use force flag to override.")

        if extract and file_path.suffix == ".zip":                  # Determine whether to extract a zip
            extracted_files = extract_archive(file_path)            # If needed extract and return the list of files.
            files.extend(extracted_files)                           # Add extracted to the list of downloaded files.
        else:
            files.append(str(file_path))                            # Add a single file resource (not zip) to the list.

    if len(files) == 1:     # If a single file was downloaded
        files = files[0]    # return the file path (instead of a list).

    return files


def _get_cache_path(entity_id: str, is_dataset: bool) -> Path:
    """
    Get a file cache path.
    :param entity_id: Dataset or resource id.
    :param is_dataset: A flag indicating if it is a dataset (package).
    :return: Cache file path object.
    """
    cache_dir = Path(user_cache_dir("rastertools"))                         # Get cache root dir.
    cache_dir.mkdir(exist_ok=True)                                          # Make sure it exists.
    entity_type = "package" if is_dataset else "resource"                   # Determine subdir name.
    return cache_dir.joinpath(entity_type).joinpath(f"{entity_id}.json")    # Construct the path.


def get_metadata(remote: RemoteCKAN, entity_id: str, is_dataset: bool = True) -> Dict:
    """
    Get GDx entity metadata via GDx API call. Entity can be a dataset (aka package) or a resource.
    :param remote: CKAN remote object.
    :param entity_id: GDx entity id.
    :param is_dataset: Flag indicating whether to treat id as a dataset or a resource.
    :return: Entity metadata as a dictionary.
    """
    try:
        show_action = remote.action.package_show if is_dataset else remote.action.resource_show  # Pick CKAN API func.
        meta = show_action(id=entity_id)                                    # Make GDx API call
        save_json(meta, json_path=_get_cache_path(entity_id, is_dataset))   # Save metadata to cache
    except requests.exceptions.ConnectionError as ex:                       # If GDx connection failed
        meta_path = _get_cache_path(entity_id, is_dataset)                  # Get entity metadata from cache
        meta = read_json(meta_path) if meta_path.is_file() else None        # and read it.
    return meta


def _download_url_to_file(remote: RemoteCKAN, url: str, file_path: Union[str, Path]) -> None:
    """
    Downloads a GDx resource by submitting a request to the specified GDx url.
    :param remote: CKAN remote object.
    :param url: Resource GDx url, obtained from the resource metadata (retried by a previous API call or from cache).
    :param file_path: File path were to store the downloaded resource.
    :return: None
    """
    file_obj = requests.get(url=url,
                            headers={'Authorization': remote.apikey},
                            allow_redirects=True,
                            params={'sensitive': 'true'})
    # Save file locally
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(str(file_path), 'wb') as fid01:
        fid01.write(file_obj.content)


def get_file_path(meta: Dict, data_dir: Union[str, Path], prefix: str, suffix: str) -> Union[Path, None]:
    """
    Construct resource local file path or return None if resource name doesn't meet the prefix/suffix filter.
    :param meta: Resource metadata, obtained with a previous CKAN API call.
    :param data_dir: Root dir path.
    :param prefix: Prefix used to filter resources by name prefix.
    :param suffix: Suffix used to filter resources by name suffix.
    :return: File Path object or None (if filtered out).
    """
    file_name = meta['name']
    if "." not in file_name:
        file_name = f"{file_name}.{meta['format']}".lower()

    file_path = Path(data_dir).joinpath(file_name)

    prefix_ok = prefix is None or file_name.startswith(prefix)  # If prefix is specified and filter by prefix.
    suffix_ok = suffix is None or file_name.endswith(suffix)    # If suffix is specified and filter by suffix.
    return file_path if prefix_ok and suffix_ok else None       # Return file path if filters are OK.


