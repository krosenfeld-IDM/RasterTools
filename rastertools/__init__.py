
from .version import __version__, __versiondate__, __license__
from rastertools.raster import raster_clip, raster_clip_weighted
from rastertools.shape import shape_subdivide


# module level doc-string
__doc__ = """
**rastertools** package provides features for extracting data from raster files using shapes/geometries as selectors.  
"""

# Use __all__ to let type checkers know what is part of the public API.
_all_ = ['raster_clip', 'raster_clip_weighted', 'shape_subdivide']

