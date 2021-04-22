#!/usr/bin/env python3

"""
This script should not be used in any serious way (in its current form at least)!
It's just a way for us to learn how to use pyGMT and how to read/write the sample data.
"""

from pygmt import blockmedian, surface, grdtrack, grdcut, grdfilter
import os
import pandas as pd
import matplotlib.pyplot as plt
import argparse

from loaders import load_source
from grid import Grid

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

def min_regions(region1, region2):
    """Returns the smaller of the two regions (i.e. the intersection)"""
    return [max(region1[0], region2[0]), min(region1[1], region2[1]), max(region1[2], region2[2]), min(region1[3], region2[3])]

def resample_grid(in_fname, out_fname, region, spacing):
    """Resamples the grid using grdsample. Note that this operates on external files, not on already loaded grids."""
    os.system(f'gmt grdsample {in_fname} -G{out_fname} -R{region_to_str(region)} -I{spacing} -V')

def calc_diff_grid(base_grid, update_grid, diff_threshold=0.0):
    """Calculates difference grid for use in remove-restore"""
    print("Blockmedian update grid")
    max_spacing = max(update_grid.spacing, base_grid.spacing)
    minimal_region = min_regions(update_grid.region, base_grid.region)
    bmd = blockmedian(update_grid.xyz, spacing=max_spacing, region=minimal_region)

    print("Find z in base grid")
    base_pts = grdtrack(bmd, base_grid.grid, 'base_z', interpolation='l')

    print ("Create difference grid")
    diff = pd.DataFrame()
    diff['x'] = base_pts['x']
    diff['y'] = base_pts['y']
    diff['z'] = base_pts['z'] - base_pts['base_z']

    diff[diff.z.abs() < diff_threshold]['z'] = 0.0 # Filter out small differences

    diff_xyz_fname = "diff.xyz"
    diff_grid_fname = "diff.nc"
    diff.to_csv(diff_xyz_fname, sep=' ', header=False, index=False)

    os.system(f'gmt nearneighbor {diff_xyz_fname} -G{diff_grid_fname} -R{region_to_str(base_grid.region)} -I{base_grid.spacing} -S{2*max_spacing} -N4 -E0 -V')
    diff_grid, _, _ = load_source(diff_grid_fname)

    # Cleanup files
    os.remove(diff_grid_fname)
    os.remove(diff_xyz_fname)

    return diff_grid


def main():
    # Handle arguments
    parser = argparse.ArgumentParser(description='Combine multiple bathymmetry sources into a single grid')
    parser.add_argument('filenames', nargs='+', help='sources to combine with the base grid')
    parser.add_argument('--base', required=True, help='base grid')
    parser.add_argument('--spacing', type=float, help='output grid spacing')
    parser.add_argument('--diff_threshold', default=0.0, help='value above which differences will be added to the base grid')
    parser.add_argument('--output', required=True, help='filename of final output')
    args = parser.parse_args()

    filenames = args.filenames
    base_fname = args.base
    diff_threshold = args.diff_threshold
    output_fname = args.output
    region_of_interest = [-123.3, -122.8, 48.700, 48.900] # TODO make this a parameter

    # Create base grid
    if args.spacing:
        spacing = args.spacing
        print(f"Regridding base grid to spacing {spacing}")
        resampled_base_fname = 'base_grid_resampled.nc'
        resample_grid(base_fname, resampled_base_fname, region_of_interest, spacing)
        base_grid = Grid(resampled_base_fname, convert_to_xyz=False)
        os.remove(resampled_base_fname)
    else:
        base_grid = Grid(base_fname, convert_to_xyz=False)
        base_grid.grdcut(region_of_interest)

    fig, axes = plt.subplots(2,2)
    base_grid.plot(ax=axes[0,0])

    # Update base grid
    for fname in filenames:
        print("Loading update grid")
        update_grid = Grid(fname, convert_to_xyz=True)

        diff_grid = calc_diff_grid(base_grid, update_grid, diff_threshold=diff_threshold)

        print("Update base grid")
        base_grid.grid.values += diff_grid.values

    base_grid.plot(ax=axes[0,1])
    base_grid.grid.differentiate('x').plot(ax=axes[1,0])
    base_grid.grid.differentiate('y').plot(ax=axes[1,1])
    plt.show()

    base_grid.save_grid(args.output)

if __name__ == "__main__":
    main()
