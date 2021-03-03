#!/usr/bin/env python3

"""
This script should not be used in any serious way (in its current form at least)!
It's just a way for us to learn how to use pyGMT and how to read/write the sample data.
"""

from pygmt import blockmedian
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import argparse

def load_source(filepath):
    xr_data = xr.open_dataarray(filepath)
    # we might lose some metadata with the `to_dataframe()` conversion here, but that's OK as we'll just want a bunch of xyz
    # independent of the original data file here in the future. Good to keep in mind, though, and ensure that the metadata
    # is correct and in the right unit etc.
    xyz_data = xr_data.to_dataframe()
    xyz_data = xyz_data.reset_index()
    xyz_data.rename(columns={'lon': 'x', 'lat': 'y', 'elevation': 'z'}, inplace=True)
    xyz_data = xyz_data[['x', 'y', 'z']]  # `blockmedian()` requires columns in the right order!!!
    return xyz_data

def main():
    # Handle arguments
    parser = argparse.ArgumentParser(description='Combine multiple bathymmetry sources into a single grid')
    parser.add_argument('filenames', nargs='+',
                        help='sources to combine')
    args = parser.parse_args()

    filenames = args.filenames
    filepath = filenames[0]

    xyz_data = load_source(filepath)

    region = [-127, -122, 47, 49]  # area of interest
    bmd = blockmedian(xyz_data, spacing=0.05, region=region)  # TODO what unit is the spacing???

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    # ax.scatter(xs=xyz_data['x'], ys=xyz_data['y'], zs=xyz_data['z'], s=0.1)
    ax.scatter(xs=bmd['x'], ys=bmd['y'], zs=bmd['z'])

    plt.show()

if __name__ == "__main__":
    main()
