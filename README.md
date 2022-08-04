# RasterTools
Python package for processing raster (for example, extracting admin shape population from a raster file).    

## Setup  
Clone or download this GitHub repo and `cd` to the repo root.  
```bash
git clone git@github.com:InstituteforDiseaseModeling/RasterTools.git  
cd RasterTools  
```
  
Create a Python virtual environment using the preferred tool (here we use Anaconda).    
  
```bash
conda create --name  rastertools python=3.9 -c conda-forge  
conda activate rastertools  
```
  
Install the requirements and the package (here in dev mode).  
```bash
conda install --file requirements.txt -c conda-forge  
pip install -e .   
```

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
