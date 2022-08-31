import shutil
import tempfile
import unittest

from pathlib import Path


class ShapeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        shutil.rmtree(self.test_dir, ignore_errors=True)

    # def test_area_sphere(self):
    #     world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    #     actual = area_sphere(world)
    #     crs = world.crs
    #     #expected = world[""].area
    #     pass