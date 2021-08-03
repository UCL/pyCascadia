"""
Helper functions for loading different types of data sources as xarray grids
"""

import xarray as xr
from typing import Tuple
import matplotlib.pyplot as plt


def load_source(filepath: str, plot: bool = False) -> Tuple[xr.DataArray, list, float]:
    """Loads an xarray dataarray from file

    Supported file formats are:
        - GeoTiff
        - netCDF

    Args:
        filepath: name of file to load
        plot: whether to plot loaded grid

    Returns:
        - grid as xarray DataArray
        - bounding region of grid
        - grid spacing
    """
    print(f"Loading {filepath}")
    ext = filepath.split(".")[-1]
    if ext == "nc":
        xr_data = load_netcdf(filepath)
    elif ext == "tif" or ext == "tiff":
        xr_data = load_geotiff(filepath)
    else:
        raise RuntimeError(f"Error: filetype {ext} not recognised.")

    xr_data = xr_data.astype("float32")

    if plot:
        xr_data.plot()
        plt.show()

    region = extract_region(xr_data)
    spacing = extract_spacing(xr_data)

    print(f"Input region: {region}")
    print(f"Input spacing: {spacing}")

    return xr_data, region, spacing


def extract_region(xr_data: xr.DataArray) -> list:
    """Extracts the bounding box from an xarray dataarray

    Args:
        xr_data: array containing grid

    Returns:
        Bounding region of grid
    """
    left = float(xr_data.x.min())
    right = float(xr_data.x.max())
    top = float(xr_data.y.max())
    bottom = float(xr_data.y.min())

    return [left, right, bottom, top]


def extract_spacing(xr_data: xr.DataArray) -> float:
    """Extracts spacing from xarray dataarray.

    This assumes the grid spacing is identical in both x & y directions.

    Args:
        xr_data: array containing grid

    Returns:
        grid spacing
    """
    return abs(float(xr_data.x[1] - xr_data.x[0]))


def load_netcdf(filepath: str) -> xr.DataArray:
    """Loads netcdf file

    Args:
        filepath: file to load

    Returns:
        grid as xarray array
    """
    xr_data = xr.open_dataarray(filepath)
    xr_data = xr_data.rename("z")
    if "lon" in xr_data.dims:
        # assume lat is also a dimension
        xr_data = xr_data.rename({"lon": "x", "lat": "y"})

    print(f"Resolution: {xr_data.values.shape}")

    return xr_data


def load_geotiff(filepath: str) -> xr.DataArray:
    """Loads geotiff file

    Args:
        filepath: file to load

    Returns:
        grid as xarray array
    """
    xr_data = xr.open_rasterio(filepath, parse_coordinates=True)
    xr_data = xr_data.squeeze("band")  # Remove band if present
    del xr_data["band"]
    xr_data = xr_data.rename("z")

    print(f"Resolution: ({xr_data.sizes['x']}, {xr_data.sizes['y']})")
    print(f"CRS: {xr_data.crs}")

    # Sort by y coord because rasterio loads the file "upside down"
    xr_data = xr_data.sortby("y")

    return xr_data
