import unittest

import numpy as np

from shapely.geometry import Polygon

from rastertools import ShapeView, area_sphere, centroid_area
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

        # centroid
        self.assertAlmostEqual(shp.center[0], 27.86319, places=4)
        self.assertAlmostEqual(shp.center[1], -11.75417, places=4)

    def test_area_sphere(self):
        """Testing the function for calculating shape sphere area."""
        parts = self.one_shape.shape.parts
        actual_area = area_sphere(self.one_shape.points[parts[0]:parts[1]])
        self.assertAlmostEqual(actual_area, 729.4676671307703, places=4)

    def test_centroid_area_all_shapes(self):
        """Testing the function for calculating shape centroid."""
        shapes = ShapeView.from_file(self.shape_file)

        for shp in shapes:
            prt_list = list(shp.shape.parts) + [len(shp.points)]
            for i in range(len(prt_list) - 1):
                # Skip a known edge case (see "test_centroid_area_edge_case")
                if shp.name == "AFRO:DRCONGO:HAUT_KATANGA:KAMPEMBA" and i == 1:
                    continue

                points = shp.points[prt_list[i]:prt_list[i + 1]]
                self.validate_centroid(points, places=4)

    def test_centroid_area_edge_case(self):
        points = np.array([
            [27.67629337, - 11.57355617],
            [27.67629332, - 11.57355617],
            [27.6754073, -11.57303985],
            [27.67629337, - 11.57355617]
        ])

        self.validate_centroid(points, places=2)  # fails for places=3 or higher

    def validate_centroid(self, points, places=4):
        """Compare centroid coordinates and area with shapley."""
        # actual centroid
        x1, y1, a1 = centroid_area(points)

        # expected centroid (from Shapely)
        p = Polygon(points)
        c = p.centroid
        x2, y2, a2 = c.xy[0][0], c.xy[1][0], p.area

        self.assertAlmostEqual(x1, x2, places=places)
        self.assertAlmostEqual(y1, y2, places=places)
        self.assertAlmostEqual(abs(a1), a2, places=places)


if __name__ == '__main__':
    unittest.main()
