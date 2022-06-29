
from rastertools.etl import extract
from rastertools.utils import download

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
_all_ = ['extract']
