
from rastertools.data import download, get_remote
from rastertools.raster import raster_clip
from rastertools.shape import area_sphere
from rastertools.etl import zonal_stats


# module level doc-string
__doc__ = """
**rastertools** package provides features for extracting data from raster files using shapes/geometries as selectors.  
Main Features
-------------
- Process a single or multiple raster files
- Add raster file metadata to the resulting dataframe.
- Use GeoPandas representative_point features to add admin location representative points.
- Use GeoPandas dissolve feature to apply zonal statistics on specified administrative level.
"""

# Use __all__ to let type checkers know what is part of the public API.
_all_ = ['get_remote', 'download', 'zonal_stats', 'raster_clip', 'area_sphere']

