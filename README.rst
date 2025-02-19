RasterTools
===========

A Python package for processing rasters with minimal dependencies. For example, with rastertools you can extract populations corresponding to an administrative shapefile from a raster file.

Setup 
-----
#. Clone or download this GitHub repo and `cd` to the repo root.::
    
    git clone git@github.com:InstituteforDiseaseModeling/RasterTools.git  
    cd RasterTools

  
#. Create a Python virtual environment using the preferred tool (here we use Anaconda).::

    conda create --name rastertools python=3.9
    conda activate rastertools  
  
#. Install this package in mode (this also installs all the requirements).::

    pip install .   


Getting Started
---------------

A typical ```raster_clip``` API usage scenario looks like this::

    from rastertools import raster_clip

    # Clipping raster with shapes  
    pop_dict = raster_clip(raster_file, shape_file)  


See the complete code in the [WorldPop example](examples/worldpop/worldpop_clipping.py).  

A typical ``shape_subdivide`` API usage scenario looks like this:: 

    from rastertools import shape_subdivide

    # Create shape subdivision layer
    subdiv_stem = shape_subdivide(shape_stem=shape_file)


See the complete code in the [Shape Subdivision example](examples/shape_subdivide/shape_subdivision.py).

Running Tests
-------------

Functional tests:

Install additional packages (like pytest): :

    # Install packages
    pip install -r requirements-test.txt


Run ``pytest`` command::

    # Run unit tests (recommended during development)
    pytest -m unit -v

    # Run test for a specific module, for example
    pytest tests/test_shape.py -v     # run shape unit tests
    pytest tests/test_download.py -v  # run GDx download tests

    # All tests (before a commit or merging a PR)
    pytest -v

