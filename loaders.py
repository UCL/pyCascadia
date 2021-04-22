import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

"""
Helper functions for loading different types of data sources as xyz dataframes
"""

def load_source(filepath, plot=False, convert_to_xyz=False, filter_nodata=True):
    """
    Loads an xarray dataarray from file, optionally converting it to an xyz dataframe
    """
    print(f"Loading {filepath}")
    ext = filepath.split('.')[-1]
    if ext == 'nc':
        xr_data = load_netcdf(filepath)
    elif ext == 'tif' or ext == 'tiff':
        xr_data = load_geotiff(filepath)
    else:
        raise RuntimeError(f"Error: filetype {ext} not recognised.")

    if plot:
        xr_data.plot()
        plt.show()

    region = extract_region(xr_data)
    spacing = extract_spacing(xr_data)

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
    return abs(float(xr_data.y[1] - xr_data.y[0]))

def xr_to_xyz(xr_data):
    """
    Converts an xarray dataarray into a pandas dataframe.
    This requires the input coordinates to be named (x,y) and the elevation to be named z
    """
    xyz_data = xr_data.to_dataframe()
    xyz_data = xyz_data.reset_index()
    xyz_data = xyz_data[['x', 'y', 'z']]
    return xyz_data

def filter_nodata(xyz_data, nodatavals):
    """Removes values in nodatavals from input"""
    for nodata_val in nodatavals:
        xyz_data.where(xyz_data['z'] != nodata_val, inplace=True)

def load_netcdf(filepath):
    """Loads netcdf file"""
    xr_data = xr.open_dataarray(filepath).astype('float32')
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
    xr_data = xr_data.rename('z')

    print(f"Number of bands: {xr_data.coords['band'].values}")
    print(f"Resolution: ({xr_data.sizes['x']}, {xr_data.sizes['y']})")
    print(f"CRS: {xr_data.crs}")

    return xr_data
