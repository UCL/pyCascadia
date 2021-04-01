import xarray as xr
import pandas as pd
import numpy as np
import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt

"""
Helper functions for loading different types of data sources as xyz dataframes
"""

def load_source(filepath, plot=False):
    print(f"Loading {filepath}")
    ext = filepath.split('.')[-1]
    if ext == 'nc':
        return load_netcdf(filepath, plot)
    elif ext == 'tif' or ext == 'tiff':
        return load_geotiff(filepath, plot)
    else:
        raise RuntimeError(f"Error: filetype {ext} not recognised.")

def load_netcdf(filepath, plot=False, convert_to_xyz=False):
    xr_data = xr.open_dataarray(filepath)

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

def load_geotiff(filepath, plot=False):
    """Loads geotiff file as GMT-consumable pandas dataframe"""

    dataset = rasterio.open(filepath)
    print(f"Number of bands: {dataset.count}")
    print(f"Resolution: {dataset.width}, {dataset.height}")
    print(f"CRS: {dataset.crs}")

    if plot:
        show(dataset)

    # bounds go from top-left corner of top-left pixel area 
    # to bottom-right corner of bottom-right pixel area
    bounds = dataset.bounds
    left = bounds.left
    right = bounds.right
    top = bounds.top
    bottom = bounds.bottom

    x_res = dataset.width
    y_res = dataset.height

    dx = abs(right - left)/x_res
    dy = abs(top - bottom)/y_res

    # Get centre position of pixels
    x = np.linspace(left+dx/2, right-dx/2, x_res)
    y = np.linspace(top-dy/2, bottom+dy/2, y_res)

    # Form array of points
    x, y = np.meshgrid(x, y)
    z = dataset.read()

    # Convert to dataframe
    df = pd.DataFrame()
    df['x'] = x.flatten()
    df['y'] = y.flatten()
    df['z'] = z.flatten()

    region = [bounds.left, bounds.right, bounds.bottom, bounds.top]
    dataset.close()
    
    return df, region
