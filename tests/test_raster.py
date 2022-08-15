import shutil
import tempfile
import unittest

from rastertools import *
from pathlib import Path


class RasterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        shutil.rmtree(self.test_dir, ignore_errors=True)

    # def test_clip(self):
    #     cli