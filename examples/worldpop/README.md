# Extracting Population from WorldPop Rasters using GADM Shapes 

This example shows how to use `rastertools` package to extract population data from WorldPop raster files.

To run:
1. Make sure you have an [API token](https://dataexchange.gatesfoundation.org/pages/support-api-tokens#tokens) for the
Gates Data Exchange placed in a `gdx.key` file in the repo main directory.
2. Run the data generation scripts:

```bash
python worldpop_clipping.py
python worldpop_zonal_stats.py
```
3. Run the comparison scripts:
```bash
python compare.py
```

