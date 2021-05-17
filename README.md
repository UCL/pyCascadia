# pyCascadia
Implementation of GEBCO cookbook remove-restore and other cleaning of topography/bathymetry. Uses `pyGMT`.

## Installation
Some dependencies of the package are a bit fiddly to install, especially on Windows.
We recommend to use a conda environment, and install the more difficult dependencies through `conda-forge`,
by running the commands below in sequence:
1. Clone this GitHub repository.
```
git clone https://github.com/UCL/pyCascadia.git
```
2. In your local copy of the GitHub repository, create a conda environment (named "cascadia" here, but you might want to choose a different name) with Python 3.9. Other Python versions might also work, but the code is only actively tested with Python 3.9. This step also installs `pip`, which will be used to install the more straight-forward dependencies.
```
conda create -n cascadia python=3.9 pip
```
3. Additionally, install `pygmt`, `gdal` and `rasterio` into the "cascadia" environment via `conda-forge`. This step is needed because these packages are not available from the Python Package index (PyPi) (which is where `pip` looks by default) for all operating systems.
```
conda install -n cascadia pygmt gdal rasterio -c conda-forge
```
4. Activate the "cascadia" environment
```
conda activate cascadia
```
5. Install `pyCascadia`. This will also automatically install the remaining dependencies (a list of which can be found in [setup.cfg](https://github.com/UCL/pyCascadia/blob/main/setup.cfg)).
```
pip install .[test]
```
6. Check the installation worked by running the unit tests.
```
pytest
```
7. Once you've done your work with `pyCascadia`, you may want to deactivate the environment and return to your base python environment. You can do so by running:
```
conda deactivate
```

## Usage
Before using any part of `pyCascadia`, make sure you've got its conda environment activated (change "cascadia" to the name of your environment if you've named it differently when following the installation instructions).
```
conda activate cascadia
```
### Remove restore

`pyCascadia` provides the remove restore algorithm as a command line tool called `remove-restore`, e.g.
```
remove-restore --base gebco_base_grid.nc higher_res_grid.tiff --output merged_grid.nc
```
Input base and source grids are accepted in both GeoTiff or NetCDF formats. It is possible to provide more than one source grid, e.g with three source grids one would call:
```
remove-restore --base gebco_base_grid.nc higher_res_grid1.tiff higher_res_grid2.tiff higher_res_grid3 --output merged_grid.nc
```

For more details on these and other input arguments of `remove-restore`, run
```
remove-restore -h
```
on your command line.
For more fine-grained control of the `remove-restore` functionality, there is an example Jupyter notebook under `./notebooks/`. Note that to use this, you will need to `pip install jupyter` in the conda environment, too.

### Shape file closing

The scripts `close_boundary.py` and `generate_contour.sh` provide a way to close coastline contours when land intersects the data boundary. These files can be found in the `scripts/` subfolder of this directory, so you should navigate there to use them.
```
cd scripts/
```
Instructions for use:

Generate a new netCDF file with any land-boundaries set to $z=0$:

`python close_boundary.py --input <input.nc> --output <output.nc>`

Generate closed contours:

`grass78  --tmp-location --exec ./generate_contour.sh <input.nc> <output.shp>`
