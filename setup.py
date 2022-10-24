#!/usr/bin/env/python
"""Installation script
"""

import os
import sys

from pathlib import Path
from setuptools import setup, find_packages

# ensure the current directory is on sys.path so versioneer can be imported
# when pip uses PEP 517/518 build rules.
# https://github.com/python-versioneer/python-versioneer/issues/193
sys.path.append(str(Path(__file__).parent))

LONG_DESCRIPTION = """RasterTools project is a collection of simple tools for processing raster files and shape files.
"""

INSTALL_REQUIRES = [
    # TODO: move dependencies from
    # requirements.txt here if
    # the package will be published
]

# get all data dirs in the datasets module
data_files = []
#
# for item in os.listdir("rastertools/datasets"):
#     if not item.startswith("__"):
#         if os.path.isdir(os.path.join("rastertools/datasets/", item)):
#             data_files.append(os.path.join("datasets", item, "*"))
#         elif item.endswith(".zip"):
#             data_files.append(os.path.join("datasets", item))
#
# data_files.append("tests/data/*")


setup(
    name="rastertools",
    version="0.0.1",
    description="Raster and shape tools",
    license="",
    author="RasterTools contributors",
    author_email="",
    url="",
    project_urls={
        "Source": "https://github.com/InstituteforDiseaseModeling/RasterTools",
    },
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/x-rst",
    packages=find_packages(exclude=("tests",)),
    package_data={"rastertools": data_files},
    python_requires=">=3.8",
    install_requires=INSTALL_REQUIRES
)
