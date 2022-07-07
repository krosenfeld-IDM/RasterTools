import matplotlib.path as plt
import numpy as np
import shapefile

from osgeo import gdal
from pathlib import Path
from typing import Dict, Union
from rastertools.shape import area_sphere


def raster_clip(raster_file: Union[str, Path], shape_stem: Union[str, Path]) -> Dict[str, Union[float, int]]:
    """Extract data from a raster"""
    assert Path(raster_file).is_file(), "Raster file not found."
    # Raster data
    raster = gdal.Open(raster_file)
    rast_b01 = raster.GetRasterBand(1)

    # Shapefiles
    sf1 = shapefile.Reader(str(shape_stem))
    sf1s = sf1.shapes()
    sf1r = sf1.records()

    # Extract data from raster
    geo_dat = raster.GetGeoTransform()
    x0 = geo_dat[0]
    y0 = geo_dat[3]
    dx = geo_dat[1]
    dy = geo_dat[5]

    dat_mat = rast_b01.ReadAsArray(0, 0, rast_b01.XSize, rast_b01.YSize)
    xy_ints = np.argwhere(dat_mat > 0)
    sparce_data = np.zeros((xy_ints.shape[0], 3), dtype=float)

    # Construct sparce matrix of (long, lat, data)
    sparce_data[:, 0] = x0 + dx * xy_ints[:, 1] + dx / 2.0
    sparce_data[:, 1] = y0 + dy * xy_ints[:, 0] + dy / 2.0
    sparce_data[:, 2] = dat_mat[xy_ints[:, 0], xy_ints[:, 1]]

    # Output dictionary
    data_dict = dict()

    # Iterate of shapes in shapefile
    for k1 in range(len(sf1r)):

        # First (only) field in shapefile record is dotname
        shape_name = sf1r[k1][0]

        # Shapefile shape points
        sfsp = np.array(sf1s[k1].points)

        # Null shape; possible error in shapefile?
        if sfsp.shape[0] == 0:
            data_dict[shape_name] = 0
            print(k1 + 1, 'of', len(sf1r), shape_name, data_dict[shape_name])
            continue

        # Subset data matrix for clipping
        xy_max = np.max(sfsp, axis=0)
        xy_min = np.min(sfsp, axis=0)
        clip_bool1 = np.logical_and(sparce_data[:, 0] > xy_min[0], sparce_data[:, 1] > xy_min[1])
        clip_bool2 = np.logical_and(sparce_data[:, 0] < xy_max[0], sparce_data[:, 1] < xy_max[1])
        data_clip = sparce_data[np.logical_and(clip_bool1, clip_bool2), :]

        # No data in shape; possible error in shapefile?
        if data_clip.shape[0] == 0:
            data_dict[shape_name] = 0
            print(k1 + 1, 'of', len(sf1r), shape_name, data_dict[shape_name])
            continue

        # Track booleans (indicates if lat/long is interior)
        data_bool = np.zeros(data_clip.shape[0], dtype=bool)

        # Iterate over parts of shapefile
        for k2 in range(len(sf1s[k1].parts) - 1):
            shp_prt = sfsp[sf1s[k1].parts[k2]:sf1s[k1].parts[k2 + 1]]
            path_shp = plt.Path(shp_prt, closed=True, readonly=True)
            area_prt = area_sphere(shp_prt)

            # Union of positive areas; intersection with negative areas
            if area_prt > 0:
                data_bool = np.logical_or(data_bool, path_shp.contains_points(data_clip[:, :2]))
            else:
                data_bool = np.logical_and(data_bool, np.logical_not(path_shp.contains_points(data_clip[:, :2])))

        # Last piece of shapefile uses different indexing
        shp_prt = sfsp[sf1s[k1].parts[-1]:]
        path_shp = plt.Path(shp_prt, closed=True, readonly=True)
        area_prt = area_sphere(shp_prt)

        # Union of positive areas; intersection with negative areas
        if area_prt > 0:
            data_bool = np.logical_or(data_bool, path_shp.contains_points(data_clip[:, :2]))
        else:
            data_bool = np.logical_and(data_bool, np.logical_not(path_shp.contains_points(data_clip[:, :2])))

        # Record value to dict; print status
        data_dict[shape_name] = int(np.round(np.sum(data_clip[data_bool, 2]), 0))
        print(k1 + 1, 'of', len(sf1r), shape_name, data_dict[shape_name])

    return data_dict


