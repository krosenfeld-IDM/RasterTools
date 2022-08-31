"""
Functions for spatial processing of shape files.
"""

import numpy as np


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
