import unittest

import numpy as np

from rastertools import ShapeView, area_sphere
from typing import Dict


class ShapeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.shape_file = "data/cod_lev02_zones_test/cod_lev02_zones_test"
        self.expected_name = "AFRO:DRCONGO:HAUT_KATANGA:KAMPEMBA"

    @property
    def shapes_dict(self) -> Dict[str, ShapeView]:
        """Helper test property creating a dictionary of shape names and shape view objects."""
        return {s.name: s for s in ShapeView.from_file(self.shape_file)}

    @property
    def one_shape(self) -> ShapeView:
        """Helper test property providing a sample shape view object."""
        return self.shapes_dict[self.expected_name]

    def test_load_shapes_from_file(self):
        """Testing loading of a shape file and creating a list of shape view objects."""
        shapes = ShapeView.from_file(self.shape_file)
        self.assertGreater(len(shapes), 0)
        for shp in shapes:
            shp.validate()

    def test_shape_properties(self):
        """Testing shape view object properties."""
        shp = self.one_shape
        self.assertIsInstance(shp, ShapeView)

        # name, parts_count, areas
        self.assertEqual(self.expected_name, shp.name)
        self.assertEqual(shp.parts_count, 2)
        self.assertAlmostEqual(len(shp.areas), 2)
        self.assertAlmostEqual(shp.areas[0], 729.4676671307703, places=4)

        # xy min/max
        self.assertIsInstance(shp.xy_max, np.ndarray)
        self.assertIsInstance(shp.xy_min, np.ndarray)
        self.assertAlmostEqual(shp.xy_max[0], 28.01053, places=4)
        self.assertAlmostEqual(shp.xy_max[1], -11.57304, places=4)
        self.assertAlmostEqual(shp.xy_min[0], 27.6754073, places=4)
        self.assertAlmostEqual(shp.xy_min[1], -11.9589984, places=4)

        # points
        self.assertIsInstance(shp.points, np.ndarray)
        self.assertGreater(shp.points.shape[0], 2)
        self.assertEqual(shp.points.shape[1], 2)
        self.assertTrue(np.array_equal(shp.points[0, :], shp.points[-1, :]))

    def test_area_sphere(self):
        """Testing the function for calculating shape sphere area."""
        parts = self.one_shape.shape.parts
        actual_area = area_sphere(self.one_shape.points[parts[0]:parts[1]])
        self.assertAlmostEqual(actual_area, 729.4676671307703, places=4)


if __name__ == '__main__':
    unittest.main()
