"""
Functions for spatial processing of raster TIFF files.
"""

import matplotlib.path as plt
import numpy as np
import shapefile

from PIL import Image
from PIL.TiffTags import TAGS
from pathlib import Path
from typing import Any, Dict, List, Union, Callable
from rastertools.shape import ShapeView


def raster_clip(raster_file: Union[str, Path],
                shape_stem: Union[str, Path],
                shape_attr: str = "DOTNAME",
                summary_func: Callable = None,
                include_latlon: bool = False) -> Dict[str, Union[float, int]]:
    """
    Extract data from a raster based on shapes.
    :param raster_file: Local path to a raster file.
    :param shape_stem: Local path stem referencing a set of shape files.
    :param shape_attr: The shape attribute name to be use as output dictionary key.
    :param summary_func: Aggregation func to be used for summarizing clipped data for each shape.
    :return: Dictionary with dot names as keys and calculates aggregations as values.
    """
    assert Path(raster_file).is_file(), "Raster file not found."
    # Raster data
    raster = Image.open(raster_file)

    # Extract data from raster
    tags = get_tiff_tags(raster)
    point = tags["ModelTiepointTag"]
    scale = tags["ModelPixelScaleTag"]
    x0, y0 = point[3], point[4]
    dx, dy = scale[0], -scale[1]

    # Make sure values are in range
    assert -180 < x0 < 180, "Tie point x coordinate (longitude) have invalid range."
    assert -85 < y0 < 85, "Tie point y coordinate (latitude) have invalid range."
    assert 0 < dx < 1, "Pixel dx scale has invalid range."
    assert -1 < dy < 0, "Pixel dy scale has invalid range."

    # Init sparce data matrix
    dat_mat = np.array(raster)
    xy_ints = np.argwhere(dat_mat > 0)
    sparce_data = np.zeros((xy_ints.shape[0], 3), dtype=float)

    # Construct sparce matrix of (long, lat, data)
    sparce_data[:, 0] = x0 + dx * xy_ints[:, 1] + dx / 2.0
    sparce_data[:, 1] = y0 + dy * xy_ints[:, 0] + dy / 2.0
    sparce_data[:, 2] = dat_mat[xy_ints[:, 0], xy_ints[:, 1]]

    # Shapefiles
    shapes = ShapeView.from_file(shape_stem, shape_attr)

    # Output dictionary
    data_dict = dict()

    # Iterate of shapes in shapefile
    for k1, shp in enumerate(shapes):
        # Null shape; error in shapefile
        shp.validate()

        # Subset data matrix for clipping
        clip_bool1 = np.logical_and(sparce_data[:, 0] > shp.xy_min[0], sparce_data[:, 1] > shp.xy_min[1])
        clip_bool2 = np.logical_and(sparce_data[:, 0] < shp.xy_max[0], sparce_data[:, 1] < shp.xy_max[1])
        data_clip = sparce_data[np.logical_and(clip_bool1, clip_bool2), :]

        # No population in shape
        if data_clip.shape[0] == 0:
            if include_latlon:
                data_dict[shp.name] = {"lat": np.nan, "lon": np.nan, "pop": 0}
            else:
                data_dict[shp.name] = 0
            print(k1 + 1, 'of', len(shapes), shp.name, data_dict[shp.name])
            continue

        # Track booleans (indicates if lat/long is interior)
        data_bool = np.zeros(data_clip.shape[0], dtype=bool)

        # Iterate over parts of shapefile
        for path_shp, area_prt in zip(shp.paths, shp.areas):
            # Union of positive areas; intersection with negative areas
            if area_prt > 0:
                data_bool = np.logical_or(data_bool, path_shp.contains_points(data_clip[:, :2]))
            else:
                data_bool = np.logical_and(data_bool, np.logical_not(path_shp.contains_points(data_clip[:, :2])))

        # Record value to dict; print status
        value = data_clip[data_bool, 2]
        summary_func = summary_func or default_summary_func
        if include_latlon:
            lon = np.mean(data_clip[data_bool, 0])
            lat = np.mean(data_clip[data_bool, 1])
            data_dict[shp.name] = {"lat": lat, "lon": lon, "pop": summary_func(value)}
        else:
            data_dict[shp.name] = summary_func(value)
        print(k1 + 1, 'of', len(shapes), shp.name, data_dict[shp.name])

    return data_dict


def default_summary_func(v: np.ndarray):
    return int(np.round(np.sum(v), 0))


def get_tiff_tags(raster: Image) -> Dict[str, Any]:
    """
    Read tags from a TIFF file
    https://stackoverflow.com/questions/46477712/reading-tiff-image-metadata-in-python
    :param raster: TIFF object
    :return: Dictionary of tag names and values.
    """
    return {TAGS[t]: raster.tag[t] for t in dict(raster.tag)}
