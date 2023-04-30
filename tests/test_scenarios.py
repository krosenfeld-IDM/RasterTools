import numpy as np
import shutil
import tempfile
import pandas as pd
import pytest
import sys

from pathlib import Path
from typing import Dict, List, Union

from contextlib import suppress  # let pytest skip unsupported tests
with suppress(ImportError):
    from emod_api.demographics import Demographics as demographics
    from emod_api.demographics.Demographics import Demographics, Node

from rastertools import raster_clip
from pytest_init import change_test_dir  # don't remove 


def setup_function() -> None:
    pytest.shape_file = "data/cod_lev02_zones_test/cod_lev02_zones_test"
    pytest.raster_file = "data/cod_2012_1km_aggregated_unadj_test.tif"
    pytest.test_dir = Path(tempfile.mkdtemp())


def teardown_function() -> None:
    shutil.rmtree(pytest.test_dir)


@pytest.mark.unit
@pytest.mark.skipif('emod_api' not in sys.modules, reason="requires the 'emod_api' library")
def test_emod_demographics():
    """Testing generating demographics from extracted population."""
    # Extract pop
    actual_pop: Dict = raster_clip(pytest.raster_file, pytest.shape_file, include_latlon=True)

    # Create Demographics object
    df = pd.DataFrame.from_dict(actual_pop, orient="index").reset_index(names=["dot_name"])
    nan_count = len([v for v in list(df.lat) if np.isnan(v)])
    df = df[pd.notna(df.lat)]
    pop_csv = str(pytest.test_dir.joinpath("pop.csv"))
    df.to_csv(pop_csv, index=False)
    dmg: Demographics = demographics.from_csv(pop_csv)

    # Read nodes info from demographics dict
    validate_demographics(dmg, lats_mean=-11.7816, lons_mean=27.6145, pops_mean=177959)
    assert nan_count == 1


@pytest.mark.unit
@pytest.mark.skipif('emod_api' not in sys.modules, reason="requires the 'emod_api' library")
def test_emod_demographics_nodes():
    """Testing generating demographics from extracted population."""
    # Extract pop
    pop_dict: Dict = raster_clip(pytest.raster_file, pytest.shape_file, include_latlon=True)

    # Generate Nodes from "cleaned" pop dict
    pop_dict2 = {k: v for k, v in pop_dict.items() if not np.isnan(v["lat"]*v["lat"])}
    node_list = [(Node(name=name, **node)) for name, node in pop_dict2.items()]

    # Generate Demographics object
    dmg = Demographics(nodes=node_list, idref="RasterToolsTest")
    dmg_file = pytest.test_dir.joinpath("demographics.json")
    dmg.generate_file(name=dmg_file)

    validate_demographics(dmg, lats_mean=-11.7816, lons_mean=27.6145, pops_mean=177959)


def validate_demographics(dmg_object_or_file: Union[str, Path, Demographics],
                          lats_mean: float,
                          lons_mean: float,
                          pops_mean: float,
                          places: int = 4) -> None:
    """Basic validation of a demographics file or object."""

    if isinstance(dmg_object_or_file, str) or isinstance(dmg_object_or_file, Path):
        assert Path(dmg_object_or_file).is_file(), "Demographics file not found."
        dmg = demographics.from_file(str(dmg_object_or_file))
    elif isinstance(dmg_object_or_file, Demographics):
        dmg = dmg_object_or_file
    else:
        raise ValueError("Unsupported demographics object.")

    # Read nodes info from demographics dict
    nodes: List[Node] = dmg.to_dict()["Nodes"]
    lats: List[float] = [n["NodeAttributes"]["Latitude"] for n in nodes]
    lons: List[float] = [n["NodeAttributes"]["Longitude"] for n in nodes]
    pops: List[float] = [n["NodeAttributes"]["InitialPopulation"] for n in nodes]

    # Test lat/lon/pop stats
    actual_lats_mean: float = float(np.mean(lats))
    actual_lons_mean: float = float(np.mean(lons))
    actual_pops_mean: float = float(np.mean(pops))

    assert round(actual_lats_mean, places) == round(lats_mean, places)
    assert round(actual_lons_mean, places) == round(lons_mean, places)
    assert round(actual_pops_mean, 0) == round(pops_mean, 0)
