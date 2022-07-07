# RasterTools

Python scripts for working with shapefiles and population data

## Getting Started

### UNIX

Clone the repo and from the repo root dir install the package in dev mode
```bash
pip install -e .
```

Try the WorldPop/GADM example.
```python
cd examples/worldpop-gadm
python worldpop.py
```

### WINDOWS (ANACONDA)

Clone the repo and then create and activate an Anaconda environment (python >=3.8) using the conda-forge channel:

```bash
conda create rastertools python=3.9 -c conda-forge
conda activate rastertools
```

From the repo root directory install the requirements using the conda-forge channel:
```bash
conda install --file requirements.txt -c conda-forge
```

and then install the package in dev mode
```bash
pip install -e .
```

Try the WorldPop/GADM example.
```python
cd examples/worldpop-gadm
python worldpop.py

