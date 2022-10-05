import numpy as np
import os
import shutil
import tempfile
import unittest

from pathlib import Path
from rastertools import raster_clip, utils
from typing import Dict


class RasterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.shape_file = "data/cod_lev02_zones_test/cod_lev02_zones_test"
        self.raster_file = "data/cod_2012_1km_aggregated_unadj_test.tif"

    def test_raster_clip(self):
        """Testing raster_clip with the default stats function (sum)."""
        actual_pop: Dict = raster_clip(self.raster_file, self.shape_file)
        expected_pop: Dict = utils.read_json(Path("expected").joinpath("clipped_pop_sum.json"))
        self.assertEqual(expected_pop, actual_pop)

    def test_raster_clip_stat_fn(self):
        """Testing raster_clip with a provided stats function."""
        actual_mean_pop: Dict = raster_clip(self.raster_file, self.shape_file, summary_func=np.mean)
        expected_sum_pop: Dict = utils.read_json(Path("expected").joinpath("clipped_pop_sum.json"))
        expected_mean_pop: Dict = utils.read_json(Path("expected").joinpath("clipped_pop_mean.json"))

        for k in actual_mean_pop:
            self.assertAlmostEqual(expected_mean_pop[k], actual_mean_pop[k], places=4)
            self.assertGreaterEqual(expected_sum_pop[k], int(actual_mean_pop[k]))


if __name__ == '__main__':
    unittest.main()
