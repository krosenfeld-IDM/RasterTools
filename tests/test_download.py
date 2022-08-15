import shutil
import tempfile
import unittest
from rastertools import *
from pathlib import Path


class DownloadTests(unittest.TestCase):
    def setUp(self) -> None:
        self.gdx = get_remote(str(Path(__file__).parent.parent.joinpath("gdx.key")))
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_download_single_resource(self):
        file_path = download("1a9ee752-e92b-4ce4-87c1-21106c1a4310", data_dir=str(self.test_dir), remote=self.gdx)
        self.assertTrue(Path(file_path).is_file())

    def test_download_dataset(self):
        file_paths = download("f009840c-d8d0-4acd-b928-200a0b36ba05", dataset=True, prefix="ewB", suffix=".csv", data_dir=str(self.test_dir), remote=self.gdx)
        self.assertEquals(sorted(file_paths), sorted([str(f) for f in list(self.test_dir.glob("*.csv"))]))
        for f in file_paths:
            self.assertTrue(Path(f).is_file())
