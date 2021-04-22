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

def main():
    # Handle arguments
    parser = argparse.ArgumentParser(description='Combine multiple bathymmetry sources into a single grid')
    parser.add_argument('filenames', nargs='+', help='sources to combine with the base grid')
    parser.add_argument('--base', required=True, help='base grid')
    parser.add_argument('--regrid_base', action='store_true', help='base grid')
    parser.add_argument('--spacing', type=float, help='output grid spacing')
    parser.add_argument('--difference_threshold', default=0.0, help='value above which differences will be added to the base grid')
    args = parser.parse_args()

    filenames = args.filenames
    base_filepath = args.base
    filepath = filenames[0]
    region_of_interest = [-123.3, -122.8, 48.700, 48.900] # TODO make this a parameter

    # Create base grid
    if args.spacing:
        spacing = args.spacing
        print(f"Regridding base grid to spacing {spacing}")
        resampled_base_fname = 'base_grid_resampled.nc'
        os.system(f'gmt grdsample {base_filepath} -G{resampled_base_fname} -R{region_to_str(region_of_interest)} -I{spacing} -V')
        base_grid, base_region, _ = load_source(
            resampled_base_fname, convert_to_xyz=False
        )
        os.remove(resampled_base_fname)
    else:
        base_grid, initial_base_region, spacing = load_source(
            base_filepath, convert_to_xyz=False
        )
        base_grid = grdcut(base_grid, region=region_of_interest) # crop grid

    print("Loading update grid")
    xyz_data, region, update_spacing = load_source(filepath, plot=False, convert_to_xyz=True)

    minimal_region = min_regions(region, region_of_interest)

    print("Blockmedian update grid")
    bmd_spacing = max(update_spacing, spacing)
    print(spacing, update_spacing, bmd_spacing)
    bmd = blockmedian(xyz_data, spacing=bmd_spacing, region=minimal_region)

    print("Find z in base grid")
    base_pts = grdtrack(bmd, base_grid, 'base_z', interpolation='l')

    print ("Create difference grid")
    diff = pd.DataFrame()
    diff['x'] = base_pts['x']
    diff['y'] = base_pts['y']
    diff['z'] = base_pts['z'] - base_pts['base_z']

    diff.drop(diff[diff.z.abs() < args.difference_threshold].index, inplace=True) # Filter out small differences

    diff_xyz_fname = "diff.xyz"
    diff_grid_fname = "diff.nc"
    diff.to_csv(diff_xyz_fname, sep=' ', header=False, index=False)

    base_region = extract_region(base_grid) # must be calcd from base grid to properly align grids
    os.system(f'gmt nearneighbor {diff_xyz_fname} -G{diff_grid_fname} -R{region_to_str(base_region)} -I{spacing} -S{2*bmd_spacing} -N4 -E0 -V')
    filtered_update, _, _ = load_source(diff_grid_fname)

    # Cleanup files
    os.remove(diff_grid_fname)
    os.remove(diff_xyz_fname)

    print("Update base grid")
    base_grid.values += filtered_update.values

    fig, axes = plt.subplots(2,2)
    base_grid.plot(ax=axes[0,0])
    filtered_update.plot(ax=axes[0,1])
    base_grid.differentiate('x').plot(ax=axes[1,0])
    base_grid.differentiate('y').plot(ax=axes[1,1])
    plt.show()

if __name__ == "__main__":
    main()
