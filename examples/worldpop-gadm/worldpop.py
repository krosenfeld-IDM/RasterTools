#!/usr/bin/env python

import pandas as pd
import geopandas as gpd

from pathlib import Path
from typing import Dict

from rastertools import download, extract


# Download WorldPop files and prepare the raster files list.
print("Download WorldPop files")
pop_url = "https://data.worldpop.org/GIS/Population/Global_2000_2020/{year}/MWI/mwi_ppp_{year}.tif"
rasters: Dict[int, Path] = {year: download(pop_url.format(year=year), "data") for year in [2018, 2019, 2020]}

# Download GAMD 3.6 shapes
print("Download GAMD 3.6 files")
gadm_file = "data/gadm36_MWI.gpkg"
gadm_url = "https://biogeo.ucdavis.edu/data/gadm3.6/gpkg/gadm36_MWI_gpkg.zip"
download(gadm_url, path="data",  extract=True)

# Extract population from WorldPop using GADM shapes as selectors.
print("Extracting population data from WorldPop")
df: pd.DataFrame = extract(rasters=rasters,
                           shapes=gpd.read_file(gadm_file),
                           adm_cols=['NAME_0', 'NAME_1', 'NAME_2'],
                           stats_cols={"sum": "pop"})

# Convert pop column to integer (keeping NaN values if they exist).
df['pop'] = df['pop'].round(0).astype('Int64')

# Save pop data to a .csv file.
output_file = "pop.csv"
df.to_csv(output_file, index=False)
print(f"Population data saved in {output_file}")

