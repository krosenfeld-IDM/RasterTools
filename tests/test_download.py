import shutil
import tempfile
import unittest
from rastertools import download, get_remote
from pathlib import Path


class DownloadTests(unittest.TestCase):
    def setUp(self) -> None:
        self.gdx = get_remote(str(Path(__file__).parent.parent.joinpath("gdx.key")))    # Prepare test GDx remote
        self.test_dir = Path(tempfile.mkdtemp())                                        # Create test temp dir

    def tearDown(self) -> None:
        shutil.rmtree(self.test_dir, ignore_errors=True)                                # Remove test temp dir

    def test_download_single_resource(self):
        """Testing the download of a single resource from GDx."""
        file_path = download("1a9ee752-e92b-4ce4-87c1-21106c1a4310", data_dir=str(self.test_dir), remote=self.gdx)
        self.assertTrue(Path(file_path).is_file())

    def test_download_dataset(self):
        """Testing the download of a dataset from GDx, containing several resources."""
        # Download the dataset and use prefix/suffix filters to download only a subset of resource.
        file_paths = download("f009840c-d8d0-4acd-b928-200a0b36ba05",
                              is_dataset=True,
                              prefix="ewB",
                              suffix=".csv",
                              data_dir=str(self.test_dir),
                              remote=self.gdx)

        # Confirm all files are successfully downloaded.
        self.assertEquals(sorted(file_paths), sorted([str(f) for f in list(self.test_dir.glob("*.csv"))]))
        for f in file_paths:
            self.assertTrue(Path(f).is_file())


if __name__ == '__main__':
    unittest.main()
