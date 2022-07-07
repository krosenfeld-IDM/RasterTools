#!/usr/bin/env python

import geopandas as gpd
import pandas as pd
import rasterstats

from pathlib import Path
from typing import Callable, Dict, List, Union


def _zonal_stats(
        raster,
        gdf: gpd.GeoDataFrame,
        stats_cols: Dict,
        band: int = None,
        affine: Dict = None,
        geom_transform: Callable[[], gpd.GeoSeries] = None,
        adm_cols: List = None,
        representative_points: bool = False,
        nodata: int = None) -> pd.DataFrame:
    """
        Calculate single raster zonal stats using shapes as selectors.
        @param gdf: GeoPandas dataframe containing administrative shapes.
        @param raster: Raster file path or (view).
        @param stats_cols: Dict mapping stat function to dataframe column name.
        @param band: Raster band id.
        @param affine: Raster transform info.
        @param geom_transform: Method to transform geometries before zone stats calculating.
        @param adm_cols: The list of admin columns.
        @param representative_points: Add representative points (lat and lon columns).
        @param nodata: No data value.
        @return:
        Pandas dataframe containing shape center points and calculated means values.
        """
    adm_cols = adm_cols or [c for c in list(gdf.columns.values) if c != "geometry"]
    cols = adm_cols + ["geometry"]

    if gdf.crs is None:
        gdf.crs = "EPSG:4326"

    gdf = gdf[cols].dissolve(adm_cols, as_index=False)

    if type(raster) == str:
        assert Path(raster).exists(), "Raster not found."

    # Re-project shapes and find representative points, to be used as node coordinates.
    # Note, shape centroids may not be the right choice for every scenario.
    geometries: gpd.GeoSeries = gdf['geometry'].to_crs(epsg=900913)  # Choose projection that best fits your area.
    if representative_points:   # Add lat, lon columns to GeoDataframe
        cnt = geometries.representative_point().to_crs(epsg=4326)  # Re-project back to get longitude/latitude
        gdf["lon"] = cnt.apply(lambda r: round(r.x, 6))
        gdf["lat"] = cnt.apply(lambda r: round(r.y, 6))
        cols.extend(["lon", "lat"])

    # Transform geometries if function is given as an argument.
    if geom_transform is not None:
        gmt = geom_transform(geometries).to_crs(epsg=4326)
        gdf = gdf.set_geometry(gmt)

    # Calculate zonal statistics.
    stats = stats_cols.keys()
    zs = rasterstats.zonal_stats(gdf, raster, stats=stats, affine=affine, band_num=band, nodata=nodata, all_touched=True)
    df_zs = pd.DataFrame(zs)
    df_zs = df_zs.rename(columns=stats_cols)

    cols = adm_cols.copy() if adm_cols else []

    if band is not None:
        df_zs['band'] = band
        cols.extend(['band'])

    # Join GeoDataframe metadata with calculated zonal stats.
    # This join works based on index (df_zs was produced from gdf without modifying index).
    df = pd.DataFrame(gdf)
    df = df.join(df_zs)
    cols.extend(list(stats_cols.values()))

    df = df[cols].copy()

    return df


def zonal_stats(
        rasters: Union[Dict],                           #List, str, Path, object
        shapes: Union[gpd.GeoDataFrame, str, Path],
        stats_cols: Dict,
        band: int = None,
        affine: Dict = None,
        geom_transform: Callable[[], gpd.GeoSeries] = None,
        adm_cols: List = None,
        representative_points: bool = False,
        nodata: int = None) -> pd.DataFrame:            #Union[pd.DataFrame, str]:
    """
    Calculate rasters zonal stats using shapes as selectors.
    @param rasters:
    @param shapes: GeoPandas dataframe or file(s) containing administrative shapes.
    @param stats_cols: Dict mapping stat function to dataframe column name.
    @param band: Raster band id.
    @param affine: Raster transform info.
    @param geom_transform: Method to transform geometries before zone stats calculating.
    @param adm_cols: The list of admin columns.
    @param representative_points: Add representative points (lat and lon columns).
    @param nodata: No data value.
    @return:
    Pandas dataframe containing shape center points and calculated means values.
    """
    args = {k: v for k, v in locals().items() if k not in ["rasters", "shapes"] and not k.startswith("_")}
    df_list = []
    for info, raster in rasters.items():
        df = _zonal_stats(raster=raster, gdf=shapes, **args)
        df["info"] = info
        df_list.append(df)

    df_all = pd.concat(df_list)

    return df_all
