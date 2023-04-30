# RasterTools
Python package for processing raster (for example, extracting admin shape population from a raster file).    

## Setup  
1. Clone or download this GitHub repo and `cd` to the repo root.  
```bash
git clone git@github.com:InstituteforDiseaseModeling/RasterTools.git  
cd RasterTools
```
  
2. Create a Python virtual environment using the preferred tool (here we use Anaconda).    
  
```bash
conda create --name rastertools python=3.9
conda activate rastertools  
```
  
3. Install this package in dev mode (this also installs all the requirements).  
```bash
pip install -e .   
```

4. Obtain your GDx [API token](https://dataexchange.gatesfoundation.org/pages/support-api-tokens#tokens) and store it `CKAN_API_KEY` environment variable or `gdx.key` file (in repo root, ignored by git).

## Getting Started
A typical `raster_clip` API usage scenario looks like this:  
```python
from rastertools import download, raster_clip  

# Download data form GDX  
shape_file = download(data_id= "...shapefiles id...")   
raster_file = download(data_id= "...raster files...")  

# Clipping raster with shapes  
pop_dict = raster_clip(raster_file, shape_file)  
```

See the complete code in the [WorldPop example](examples/worldpop/worldpop_clipping.py).  

A typical `shape_subdivide` API usage scenario looks like this:  
```python
from rastertools import download, shape_subdivide

# Download data form GDX
shape_file = download(data_id= "...shapefiles id...")

# Create shape subdivision layer
subdiv_stem = shape_subdivide(shape_stem=shape_file)
```

See the complete code in the [Shape Subdivision example](examples/shape_subdivide/shape_subdivision.py).

## Running Tests

### Functional tests
Install additional packages (like emod_api and shapely): 
```bash
# Install packages
pip install -r requirements-test.txt
```

Run 'pytest' command:
```bash
# Run unit tests (recommended during development)
pytest -m unit -v

# Run test for a specific module, for example
pytest tests/test_shape.py -v     # run shape unit tests
pytest tests/test_download.py -v  # run GDx download tests

# All tests (before a commit or merging a PR)
pytest -v
```

### Tool-Comparison Tests
To run tools comparison tests install additional packages:
```bash
# Install spatial tools packages (like rasterstats, geopandas)
pip install -r requirements-tools.txt
```
Run 'pytest' command:
```bash
# Run compare tests
pytest -m compare -v
```
