import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

"""
Helper functions for loading different types of data sources
"""

def load_source(filepath, plot=False, filter_nodata=True):
    """
    Loads an xarray dataarray from file
    """
    print(f"Loading {filepath}")
    ext = filepath.split('.')[-1]
    if ext == 'nc':
        xr_data = load_netcdf(filepath)
    elif ext == 'tif' or ext == 'tiff':
        xr_data = load_geotiff(filepath)
    else:
        raise RuntimeError(f"Error: filetype {ext} not recognised.")

    xr_data = xr_data.astype('float32')

    if plot:
        xr_data.plot()
        plt.show()

    region = extract_region(xr_data)
    spacing = extract_spacing(xr_data)

    print(f"Input region: {region}")
    print(f"Input spacing: {spacing}")

    return xr_data, region, spacing


def extract_region(xr_data):
    """
    Extracts the bounding box from an xarray dataarray
    """
    left = float(xr_data.x.min())
    right = float(xr_data.x.max())
    top = float(xr_data.y.max())
    bottom = float(xr_data.y.min())

    return [left, right, bottom, top]


def extract_spacing(xr_data):
    """
    Extracts spacing from xarray dataarray (assumes same in both directions)
    """
    return abs(float(xr_data.x[1] - xr_data.x[0]))


def load_netcdf(filepath):
    """Loads netcdf file"""
    xr_data = xr.open_dataarray(filepath)
    xr_data = xr_data.rename('z')
    if 'lon' in xr_data.dims:
        # assume lat is also a dimension
        xr_data = xr_data.rename({'lon': 'x', 'lat': 'y'})

    print(f"Resolution: {xr_data.values.shape}")

    return xr_data


def load_geotiff(filepath):
    """Loads geotiff file"""
    xr_data = xr.open_rasterio(filepath, parse_coordinates=True)
    xr_data = xr_data.squeeze('band') # Remove band if present
    del xr_data['band']
    xr_data = xr_data.rename('z')

    print(f"Resolution: ({xr_data.sizes['x']}, {xr_data.sizes['y']})")
    print(f"CRS: {xr_data.crs}")

    xr_data = xr_data.sortby('y')

    return xr_data
