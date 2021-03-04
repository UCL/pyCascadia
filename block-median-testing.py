#!/usr/bin/env python3

"""
This script should not be used in any serious way (in its current form at least)!
It's just a way for us to learn how to use pyGMT and how to read/write the sample data.
"""

from pygmt import blockmedian, surface, grdtrack, grdcut
import pandas as pd
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import argparse
import rasterio
from rasterio.plot import show

def load_source(filepath):
    print(f"Loading {filepath}")
    ext = filepath.split('.')[-1]
    if ext == 'nc':
        return load_netcfd(filepath)
    elif ext == 'tif':
        return load_geotiff(filepath)
    else:
        raise RuntimeError(f"Error: filetype {ext} not recognised.")

def load_netcfd(filepath):
    xr_data = xr.open_dataarray(filepath)
    print(f"Resolution: {xr_data.values.shape}")
    # we might lose some metadata with the `to_dataframe()` conversion here, but that's OK as we'll just want a bunch of xyz
    # independent of the original data file here in the future. Good to keep in mind, though, and ensure that the metadata
    # is correct and in the right unit etc.
    xyz_data = xr_data.to_dataframe()
    xyz_data = xyz_data.reset_index()
    xyz_data.rename(columns={'lon': 'x', 'lat': 'y', 'elevation': 'z'}, inplace=True)
    xyz_data = xyz_data[['x', 'y', 'z']]  # `blockmedian()` requires columns in the right order!!!
    return xyz_data

def load_geotiff(filepath):
    """Loads geotiff file as GMT-consumable pandas dataframe"""

    dataset = rasterio.open(filepath)
    print(f"Number of bands: {dataset.count}")
    print(f"Resolution: {dataset.width}, {dataset.height}")
    print(f"CRS: {dataset.crs}")

    bounds = dataset.bounds
    left = bounds.left
    right = bounds.right
    top = bounds.top
    bottom = bounds.bottom

    x_res = dataset.width
    y_res = dataset.height

    # Get positions of upper-right corner of pixels
    x = np.linspace(left, right, x_res)
    y = np.linspace(top, bottom, y_res)

    # Recentre pixel locations
    dx = abs(right - left)/(x_res-1)
    dy = abs(top - bottom)/(y_res-1)
    x += dx/2
    y -= dy/2 # negative due to orientation of 

    # This is a test
    # ix = 0
    # iy = 0

    # pt = dataset.xy(ix, iy)
    # x_error = abs(x[ix, iy] - pt[0])
    # y_error = abs(y[ix, iy] - pt[1])

    # print(x_error, y_error)

    # Form array of points
    x, y = np.meshgrid(x, y)
    z = dataset.read()

    # Convert to dataframe
    df = pd.DataFrame()
    df['x'] = x.flatten()
    df['y'] = y.flatten()
    df['z'] = z.flatten()

    return df

def form_grid(xyz_data, region=None, spacing=None):
    """Creates grid from x,y,z points"""

    if region is None:
        raise RuntimeError("region not specified")
    if spacing is None:
        raise RuntimeError("spacing not specified")

    print("Calculating block median")
    bmd = blockmedian(xyz_data, spacing=spacing, region=region)

    print("Gridding")
    grid = surface(x=bmd['x'], y=bmd['y'], z=bmd['z'], region=region, spacing=spacing)

    return grid

def main():
    # Handle arguments
    parser = argparse.ArgumentParser(description='Combine multiple bathymmetry sources into a single grid')
    parser.add_argument('filenames', nargs='+', help='sources to combine with the base grid')
    parser.add_argument('--base', required=True, help='base grid')
    args = parser.parse_args()

    filenames = args.filenames
    base_filepath = args.base
    filepath = filenames[0]

    # Create base grid
    base_region = [-125, -122, 48, 49]  # area of interest
    spacing = 0.005

    base_xyz_data = load_source(base_filepath)
    print("Creating base grid")
    base_grid = form_grid(base_xyz_data, region=base_region, spacing=spacing)

    print("Loading update grid")
    xyz_data = load_source(filepath)
    region = [-123.8, -122.8, 48.3, 48.9] # TODO replace with automatic calc
    bmd = blockmedian(xyz_data, spacing=spacing, region=region)

    update_grid = form_grid(bmd, region=region, spacing=spacing)
    large_update_grid = grdcut(update_grid, region=base_region, extend=0.0)

    fig, axes = plt.subplots(2)
    base_grid.plot(ax=axes[0])
    axes[0].set_
    large_update_grid.plot(ax=axes[1])
    plt.show()

    print("Form difference grid")
    base_pts = grdtrack(bmd, base_grid, 'base_z')

    diff = pd.DataFrame()
    diff['x'] = base_pts['x']
    diff['y'] = base_pts['y']
    diff['z'] = base_pts['z'] - base_pts['base_z']

    diff_grid = form_grid(diff, region=region, spacing=spacing)
    large_diff_grid = grdcut(diff_grid, region=base_region, extend=0.0)

    base_grid.values += large_diff_grid.values

    fig, axes = plt.subplots(2)
    base_grid.plot(ax=axes[0])
    large_diff_grid.plot(ax=axes[1])
    plt.show()

    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection='3d')
    # # ax.scatter(xs=xyz_data['x'], ys=xyz_data['y'], zs=xyz_data['z'], s=0.1)
    # ax.scatter(xs=bmd['x'], ys=bmd['y'], zs=bmd['z'])

    # plt.show()

if __name__ == "__main__":
    main()
