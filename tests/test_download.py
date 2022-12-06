import shutil
import tempfile
import pytest

from pathlib import Path

from rastertools import download, get_remote
from pytest_init import change_test_dir  # don't remove


def setup_function() -> None:
    pytest.test_dir = Path(tempfile.mkdtemp())


def teardown_function() -> None:
    shutil.rmtree(pytest.test_dir, ignore_errors=True)  # Remove test temp dir


def gdx_key_file():
    return Path(__file__).parent.parent.joinpath("gdx.key")


@pytest.fixture()
def gdx_remote() -> None:
    return get_remote(gdx_key_file())


@pytest.mark.skipif(not gdx_key_file().is_file(), reason="GDx key file not found.")
def test_download_single_resource(gdx_remote):
    """Testing the download of a single resource from GDx."""
    file_path = download("1a9ee752-e92b-4ce4-87c1-21106c1a4310", data_dir=str(pytest.test_dir), remote=gdx_remote)
    assert Path(file_path).is_file()


@pytest.mark.skipif(not gdx_key_file().is_file(), reason="GDx key file not found.")
def test_download_dataset(gdx_remote):
    """Testing the download of a dataset from GDx, containing several resources."""
    # Download the dataset and use prefix/suffix filters to download only a subset of resource.
    file_paths = download("f009840c-d8d0-4acd-b928-200a0b36ba05",
                          is_dataset=True,
                          prefix="ewB",
                          suffix=".csv",
                          data_dir=str(pytest.test_dir),
                          remote=gdx_remote)

    # Confirm all files are successfully downloaded.
    assert sorted(file_paths) == sorted([str(f) for f in list(pytest.test_dir.glob("*.csv"))])
    for f in file_paths:
        assert Path(f).is_file()
