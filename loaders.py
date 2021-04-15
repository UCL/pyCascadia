import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

"""
Helper functions for loading different types of data sources as xyz dataframes
"""

def load_source(filepath, plot=False):
    print(f"Loading {filepath}")
    ext = filepath.split('.')[-1]
    if ext == 'nc':
        return load_netcfd(filepath, plot)
    elif ext == 'tif' or ext == 'tiff':
        return load_geotiff(filepath, plot)
    else:
        raise RuntimeError(f"Error: filetype {ext} not recognised.")

def load_netcfd(filepath, plot=False, convert_to_xyz=False):
    xr_data = xr.open_dataarray(filepath).astype('float32')

    print(f"Resolution: {xr_data.values.shape}")

    if plot:
        xr_data.plot()
        plt.show()

    if convert_to_xyz:
        # we might lose some metadata with the `to_dataframe()` conversion here, but that's OK as we'll just want a bunch of xyz
        # independent of the original data file here in the future. Good to keep in mind, though, and ensure that the metadata
        # is correct and in the right unit etc.
        xyz_data = xr_data.to_dataframe()
        xyz_data = xyz_data.reset_index()
        xyz_data.rename(columns={'lon': 'x', 'lat': 'y', 'elevation': 'z'}, inplace=True)
        xyz_data = xyz_data[['x', 'y', 'z']]  # `blockmedian()` requires columns in the right order!!!
        return xyz_data
    else:
        return xr_data

def load_geotiff(filepath, plot=False, filter_nodata=True):
    """Loads geotiff file as GMT-consumable pandas dataframe"""
    xr_data = xr.open_rasterio(filepath, parse_coordinates=True)
    xr_data = xr_data.squeeze('band') # Remove band if present
    xr_data = xr_data.rename('z')

    print(f"Number of bands: {xr_data.coords['band'].values}")
    print(f"Resolution: ({xr_data.sizes['x']}, {xr_data.sizes['y']})")
    print(f"CRS: {xr_data.crs}")

    if plot:
        xr_data.plot()
        plt.show()

    xyz_data = xr_data.to_dataframe()
    xyz_data = xyz_data.reset_index()
    xyz_data = xyz_data[['x', 'y', 'z']]

    left = xr_data.coords['x'].values[0]
    right = xr_data.coords['x'].values[-1]
    top = xr_data.coords['y'].values[0]
    bottom = xr_data.coords['y'].values[-1]

    region = [left, right, bottom, top]

    if filter_nodata:
        # filter out nodata values
        for nodata_val in xr_data.nodatavals:
            xyz_data.where(xyz_data['z'] != nodata_val, inplace=True)

    return xyz_data, region
