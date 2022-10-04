import numpy as np
import os
import shutil
import tempfile
import unittest

from pathlib import Path

import pandas as pd

from rastertools import raster_clip, utils
from typing import Dict

from emod_api.demographics import Demographics


class RasterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.shape_file = "data/cod_lev02_zones_test/cod_lev02_zones_test"
        self.raster_file = "data/cod_2012_1km_aggregated_unadj_test.tif"
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        shutil.rmtree(self.test_dir)

    def test_emod_demographics(self):
        """Testing generating demographics from extrated population."""
        # Extract pop
        actual_pop: Dict = raster_clip(self.raster_file, self.shape_file, include_latlon=True)

        # Create Demographics object
        df = pd.DataFrame.from_dict(actual_pop, orient="index").reset_index(names=["dot_name"])
        pop_csv = str(self.test_dir.joinpath("pop.csv"))
        df.to_csv(pop_csv, index=False)
        dmg: Demographics = Demographics.from_csv(pop_csv)

        # Read nodes info from demographics dict
        nodes = dmg.to_dict()["Nodes"]
        lats = [n["NodeAttributes"]["Latitude"] for n in nodes]
        lons = [n["NodeAttributes"]["Longitude"] for n in nodes]
        pops = [n["NodeAttributes"]["InitialPopulation"] for n in nodes]

        # Test lat/lon/pop stats
        lats_mean = round(np.mean([v for v in lats if not np.isnan(v)]), 2)
        lons_mean = round(np.mean([v for v in lons if not np.isnan(v)]), 2)
        pops_mean = round(np.mean([v for v in pops if not np.isnan(v)]))
        nan_count = len([v for v in lats if np.isnan(v)])

        self.assertTrue(lats_mean == -11.77)
        self.assertTrue(lons_mean == 27.6)
        self.assertTrue(pops_mean == 161781)
        self.assertTrue(nan_count == 1)


if __name__ == '__main__':
    unittest.main()
