#!/usr/bin/env python3

"""
This script should not be used in any serious way (in its current form at least)!
It's just a way for us to learn how to use pyGMT and how to read/write the sample data.
"""

from pygmt import blockmedian, surface, grdtrack, grdcut
import os
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

def region_to_str(region):
    return '/'.join(map(str, region))

def extract_region(grid):
    return [float(grid.lon[0]), float(grid.lon[-1]), float(grid.lat[0]), float(grid.lat[-1])]

def main():
    # Handle arguments
    parser = argparse.ArgumentParser(description='Combine multiple bathymmetry sources into a single grid')
    parser.add_argument('filenames', nargs='+', help='sources to combine with the base grid')
    parser.add_argument('--base', required=True, help='base grid')
    parser.add_argument('--regrid_base', action='store_true', help='base grid')
    args = parser.parse_args()

    filenames = args.filenames
    base_filepath = args.base
    filepath = filenames[0]

    nodata_val = 999999.0 # TODO can we safely add this to CLI arguments?

    # Create base grid
    # base_region = [-126, -122, 47, 49.5]  # area of interest
    base_region = [-125, -122, 48, 49]  # area of interest
    # spacing = 18/3600 # in degrees

    # base_xyz_data = load_source(base_filepath, plot=False)
    # print("Creating base grid")
    # base_grid = form_grid(base_xyz_data, region=base_region, spacing=spacing)

    base_grid = load_source(base_filepath, plot=False)
    base_grid = grdcut(base_grid, region=base_region)
    print(base_grid.lat)

    spacing = float(base_grid.lat[1] - base_grid.lat[0])

    print("Loading update grid")
    xyz_data = load_source(filepath, plot=False)
    # region = [-125, -122, 48, 49] # TODO replace with automatic calc
    region = extract_region(base_grid)
    xyz_data.where(xyz_data['z'] != nodata_val, inplace=True)

    print("Blockmedian update grid")
    bmd = blockmedian(xyz_data, spacing=spacing, region=region)

    print("Find z in base grid")
    base_pts = grdtrack(bmd, base_grid, 'base_z', interpolation='n')

    print ("Create difference grid")
    diff = pd.DataFrame()
    diff['x'] = base_pts['x']
    diff['y'] = base_pts['y']
    diff['z'] = base_pts['z'] - base_pts['base_z']

    diff_xyz_fname = "diff.xyz"
    diff_grid_fname = "diff.grd"
    diff.to_csv(diff_xyz_fname, sep=' ', header=False, index=False)

    os.system(f'gmt nearneighbor {diff_xyz_fname} -G{diff_grid_fname} -R{region_to_str(region)} -I{spacing} -S{spacing} -N4 -E0 -V')
    large_diff_grid = grdcut(diff_grid_fname, region=region, extend=0.0)
    print(large_diff_grid.y)

    print("Update base grid")
    base_grid.values += large_diff_grid.values

    fig, axes = plt.subplots(2,2)
    base_grid.plot(ax=axes[0,0])
    large_diff_grid.plot(ax=axes[0,1])
    base_grid.differentiate('lon').plot(ax=axes[1,0])
    base_grid.differentiate('lat').plot(ax=axes[1,1])
    plt.show()

if __name__ == "__main__":
    main()
