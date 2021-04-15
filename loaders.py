import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

"""
Helper functions for loading different types of data sources as xyz dataframes
"""

def load_source(filepath, plot=False, convert_to_xyz=False):
    print(f"Loading {filepath}")
    ext = filepath.split('.')[-1]
    if ext == 'nc':
        return load_netcdf(filepath, plot=plot, convert_to_xyz=convert_to_xyz)
    elif ext == 'tif' or ext == 'tiff':
        return load_geotiff(filepath, plot=plot, convert_to_xyz=convert_to_xyz)
    else:
        raise RuntimeError(f"Error: filetype {ext} not recognised.")

def extract_region(xr_data):
    left = xr_data.coords['x'].values[0]
    right = xr_data.coords['x'].values[-1]
    top = xr_data.coords['y'].values[0]
    bottom = xr_data.coords['y'].values[-1]

    return [left, right, bottom, top]

def xr_to_xyz(xr_data):
    xyz_data = xr_data.to_dataframe()
    xyz_data = xyz_data.reset_index()
    xyz_data = xyz_data[['x', 'y', 'z']]
    return xyz_data

def load_netcdf(filepath, plot=False, convert_to_xyz=False):
    xr_data = xr.open_dataarray(filepath).astype('float32')
    xr_data = xr_data.rename('z')
    xr_data = xr_data.rename({'lon': 'x', 'lat': 'y'})

    print(f"Resolution: {xr_data.values.shape}")

    if plot:
        xr_data.plot()
        plt.show()

    region = extract_region(xr_data)

    if convert_to_xyz:
        xyz_data = xr_to_xyz(xr_data)

        return xyz_data, region
    else:
        return xr_data, region

def load_geotiff(filepath, plot=False, convert_to_xyz=False, filter_nodata=True):
    xr_data = xr.open_rasterio(filepath, parse_coordinates=True)
    xr_data = xr_data.squeeze('band') # Remove band if present
    xr_data = xr_data.rename('z')

    print(f"Number of bands: {xr_data.coords['band'].values}")
    print(f"Resolution: ({xr_data.sizes['x']}, {xr_data.sizes['y']})")
    print(f"CRS: {xr_data.crs}")

    if plot:
        xr_data.plot()
        plt.show()

    region = extract_region(xr_data)

    if convert_to_xyz:
        xyz_data = xr_to_xyz(xr_data)

        if filter_nodata:
            # filter out nodata values
            for nodata_val in xr_data.nodatavals:
                xyz_data.where(xyz_data['z'] != nodata_val, inplace=True)

        return xyz_data, region
    else:
        return xr_data, region
