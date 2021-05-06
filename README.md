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
1. In your local copy of the GitHub repository, create a conda environment named "cascadia" with Python 3.9 and install `pip`, `matplotlib`, `pytest`, and `xarray`.
```
conda create -n cascadia python=3.9 pip
```
1. Additionally, install `pygmt`, `gdal` and `rasterio` into the "cascadia" environment via `conda-forge`. This step is needed because these packages are not available from the Python Package index (PyPi) (which is where `pip` looks by default) for all operating systems.
```
conda install -n cascadia pygmt gdal rasterio -c conda-forge
```
1. Activate the "cascadia" environment
```
conda activate cascadia
```
1. Install `pyCascadia`
```
pip install .
```

## Usage

### Remove restore

`pyCascadia` provides the remove restore algorithm as a command line tool called `remove-restore`, e.g.
```
remove-restore --base gebco_base_grid.nc higher_res_grid.tiff --output merged_grid.nc
```
Input base and source grids are accepted in both GeoTiff or NetCDF formats. For more details on input arguments of `remove-restore`, run
```
remove-restore -h
```
on your command line.
For more fine-grained control of the `remove-restore` functionality, there is an example Jupyter notebook under `./notebooks/`. Note that to use this, you will need to `pip install jupyter` in the conda environment, too.

### Shape file closing

The scripts `close_boundary.py` and `generate_contour.sh` provide a way to close coastline contours when land intersects the data boundary. Instructions for use:

Generate a new netCDF file with any land-boundaries set to $z=0$:

`pipenv run python close_boundary.py --input <input.nc> --output <output.nc>`

Generate closed contours:

`grass78  --tmp-location --exec ./generate_contour.sh <input.nc> <output.shp>`
