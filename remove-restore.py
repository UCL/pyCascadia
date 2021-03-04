#!/usr/bin/env python3

"""
This script should not be used in any serious way (in its current form at least)!
It's just a way for us to learn how to use pyGMT and how to read/write the sample data.
"""

from pygmt import blockmedian, surface, grdtrack, grdcut
import pandas as pd
import matplotlib.pyplot as plt
import argparse

from loaders import load_source

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
