#!/usr/bin/env python
"""
Example showing how to use rastertools API to population data from WorldPop raster using shapes and selectors.
"""

import os

from pathlib import Path
from rastertools import download, raster_clip, utils
from typing import Dict

# GDX Download
os.environ['CKAN_API_KEY'] = Path("../../gdx.key").read_text()          # GDx API KEY
shp = download("23930ae4-cd30-41b8-b33d-278a09683bac", extract=True)    # DRC health zones shapefiles
rst = download("0c7241d0-a31f-451f-9df9-f7f3eff81e03", extract=True)    # WorldPop rasters - DRC, 1km, UN adj
shape_file = Path(shp[0])
shape_file = shape_file.parent.joinpath(shape_file.stem)
raster_file = Path(rst[-1])

# Clipping raster with shapes
pop_dict: Dict = raster_clip(raster_file, shape_file)

# Save file locally
utils.save_json(pop_dict, json_path="results/clipped_pop.json", sort_keys=True)


