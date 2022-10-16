"""
Functions for spatial processing of shape files.
"""

from __future__ import annotations

import matplotlib.path as plt
import numpy as np

from pathlib import Path

from shapefile import Shape, ShapeRecord, Reader, Shapes
from typing import Any, Dict, List, Union, Callable


class ShapeView:
    """Class extracting and encapsulating shape data used for raster processing."""
    default_shape_attr: str = "DOTNAME"

    def __init__(self, shape: Shape, record: ShapeRecord, name_attr: str = None):
        self.name_attr: str = name_attr or self.default_shape_attr
        self.shape: Shape = shape
        self.record: ShapeRecord = record
        self.center: (float,float) = (0.0,0.0)
        self.paths: List[plt.Path] = []
        self.areas: List[float] = []

    def __str__(self):
        """String representation used to print or debug WeatherSet objects."""
        return f"{self.name} (parts: {str(len(self.areas))})"

    @property
    def name(self):
        """Shape name, read using name attribute."""
        return self.record[self.name_attr]

    @property
    def points(self):
        """The list of point defining shape geometry."""
        return np.array(self.shape.points)

    @property
    def xy_max(self):
        """Max x, y coordinates, based on point coordinates."""
        return np.max(self.points, axis=0)

    @property
    def xy_min(self):
        """Min x, y coordinates, based on point coordinates."""
        return np.min(self.points, axis=0)

    @property
    def parts_count(self):
        """Number of shape parts."""
        return len(self.paths)

    def validate(self) -> None:
        assert self.points.shape[0] != 0 and len(self.paths) > 0, "No parts in a shape."
        assert len(self.paths) == len(self.areas), "Inconsistent number of parts in a shape."
        assert self.name is not None and self.name != "", "Shape has no name."

    @classmethod
    def from_file(cls, shape_stem: Union[str, Path], shape_attr: Union[str, None] = None) -> List[ShapeView]:
        """
        Extract data from a raster based on shapes.
        :param shape_stem: Local path stem referencing a set of shape files.
        :param shape_attr: The shape attribute name to be use as output dictionary key.
        :return: List of ShapeView objects, containing parsed shape info.
        """
        # Shapefiles
        reader: Reader = Reader(str(shape_stem))
        sf1s: Shapes[Shape] = reader.shapes()
        sf1r: List[ShapeRecord] = reader.records()

        # Output dictionary
        shapes_data: List[cls] = []

        # Iterate of shapes in shapefile
        for k1 in range(len(sf1r)):
            # First (only) field in shapefile record is dot-name
            shp = cls(shape=sf1s[k1], record=sf1r[k1], name_attr=shape_attr)

            # List of parts in (potentially) multi-part shape
            prt_list = list(shp.shape.parts) + [len(shp.points)]

            # Accumulate total area centroid over multiple parts
            Cx_tot = Cy_tot = Axy_tot = 0.0

            # Iterate over parts of shapefile
            for k2 in range(len(prt_list) - 1):
                shp_prt = shp.points[prt_list[k2]:prt_list[k2 + 1]]
                path_shp = plt.Path(shp_prt, closed=True, readonly=True)

                # Estimate area for part
                area_prt = area_sphere(shp_prt)

                shp.paths.append(path_shp)
                shp.areas.append(area_prt)

                # Estimate area centroid for part, accumulate
                (Cx,Cy,Axy) = centroid_area(shp_prt)
                Cx_tot  += Cx*Axy
                Cy_tot  += Cy*Axy
                Axy_tot += Axy

            # Update value for area centroid
            shp.center = (Cx_tot/Axy_tot, Cy_tot/Axy_tot)

            shapes_data.append(shp)

        return shapes_data


def area_sphere(shape_points) -> float:
    """
    Calculates Area of a polygon on a sphere; JGeod (2013) v87 p43-55
    :param shape_points: point (N,2) numpy array representing a shape (first == last point, clockwise == positive)
    :return: shape area as a float
    """
    sp_rad = np.radians(shape_points)
    beta1 = sp_rad[:-1, 1]
    beta2 = sp_rad[1:, 1]
    domeg = sp_rad[1:, 0] - sp_rad[:-1, 0]

    val1 = np.tan(domeg / 2) * np.sin((beta2 + beta1) / 2.0) * np.cos((beta2 - beta1) / 2.0)
    dalph = 2.0 * np.arctan(val1)
    tarea = 6371.0 * 6371.0 * np.sum(dalph)

    return tarea


def centroid_area(shape_points) -> (float, float, float):
    """
    Calculates the area centroid of a polygon based on cartesean coordinates.
    Area calculated by this function is not a good estimate for a spherical
    polygon, and should only be used in weighting multi-part shape centroids.
    :param shape_points: point (N,2) numpy array representing a shape
                        (first == last point, clockwise == positive)
    :return: (Cx, Cy, A) Coordinates and area as floats
    """

    a_vec = (shape_points[:-1,0]*shape_points[1: ,1]-
             shape_points[1: ,0]*shape_points[:-1,1])

    A  = np.sum(a_vec)/2.0
    Cx = np.sum((shape_points[:-1,0]+shape_points[1:,0])*a_vec)/6.0/A
    Cy = np.sum((shape_points[:-1,1]+shape_points[1:,1])*a_vec)/6.0/A

    return (Cx, Cy, A)