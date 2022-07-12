#!/usr/bin/env python

import os

from pathlib import Path
from rastertools import download, raster_clip, utils
from typing import Dict

# GDX Download
os.environ['CKAN_API_KEY'] = Path("../../gdx.key").read_text()          # GDx API KEY
shp = download("23930ae4-cd30-41b8-b33d-278a09683bac", extract=True)    # DRC health zones shapefiles
rst = download("ae05eb29-b9cf-4060-a8ac-5bfe314e6199")                  # WorldPop raster - DRC 2020, 1km, UN adj
shape_file = Path(shp[0])
shape_file = shape_file.parent.joinpath(shape_file.stem)

# Clipping raster with shapes
pop_dict: Dict = raster_clip(rst, shape_file)

# Save file locally
utils.save_json(pop_dict, json_path="results/clipped_pop.json", sort_keys=True)


