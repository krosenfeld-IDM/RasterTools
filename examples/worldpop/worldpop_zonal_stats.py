#!/usr/bin/env python

import os
import pandas as pd
import geopandas as gpd

from pathlib import Path
from rastertools import download, raster_clip, zonal_stats, utils


# GDX Download
os.environ['CKAN_API_KEY'] = Path("../../gdx.key").read_text()          # GDx API KEY
shp = download("23930ae4-cd30-41b8-b33d-278a09683bac", extract=True)    # DRC health zones shapefiles
rst = download("0c7241d0-a31f-451f-9df9-f7f3eff81e03", extract=True)    # WorldPop rasters - DRC, 1km, UN adj

shape_file = [f for f in shp if Path(f).suffix == ".shp"][0]

# Extract population from WorldPop using GADM shapes as selectors.
df: pd.DataFrame = zonal_stats(rasters={2020: rst[-1]},
                               shapes=gpd.GeoDataFrame(gpd.read_file(shape_file)),
                               stats_cols={"sum": "pop"})

# Convert pop column to integer (keeping NaN values if they exist).
df['pop'] = df['pop'].round(0).astype('Int64')

# Save pop data to a .csv file.
pop_dict = df.set_index('DOTNAME').to_dict()["pop"]

for val in pop_dict:
  if(not isinstance(pop_dict[val],int)):
    pop_dict[val] = 0

# Save file locally
utils.save_json(pop_dict, json_path="results/zonal_pop.json", sort_keys=True)
