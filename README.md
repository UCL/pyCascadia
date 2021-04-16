# pyCascadia
Implementation of GEBCO cookbook remove-restore and other cleaning of topography/bathymetry. Uses `pyGMT`.

## Shape file closing

The scripts `close_boundary.py` and `generate_contour.sh` provide a way to close coastline contours when land intersects the data boundary. Instructions for use:

Generate a new netCDF file with any land-boundaries set to $z=0$:

`pipenv run python close_boundary.py --input <input.nc> --output <output.nc>`

Generate closed contours:

`grass78  --tmp-location --exec ./generate_contour.sh <input.nc> <output.shp>`
