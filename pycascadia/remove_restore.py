#!/usr/bin/env python3

"""
This script should not be used in any serious way (in its current form at least)!
It's just a way for us to learn how to use pyGMT and how to read/write the sample data.
"""

from pygmt import blockmedian, surface, grdtrack, grdfilter
import os
import pandas as pd
import matplotlib.pyplot as plt
import argparse

from pycascadia.loaders import load_source
from pycascadia.grid import Grid
from pycascadia.utility import region_to_str, min_regions

def calc_diff_grid(base_grid, update_grid, diff_threshold=0.0):
    """Calculates difference grid for use in remove-restore"""
    print("Blockmedian update grid")
    max_spacing = max(update_grid.spacing, base_grid.spacing)
    minimal_region = min_regions(update_grid.region, base_grid.region)
    bmd = blockmedian(update_grid.xyz, spacing=max_spacing, region=minimal_region)

    print("Find z in base grid")
    base_pts = grdtrack(bmd, base_grid.grid, 'base_z', interpolation='l')

    print("Create difference grid")
    diff = pd.DataFrame()
    diff['x'] = base_pts['x']
    diff['y'] = base_pts['y']
    diff['z'] = base_pts['z'] - base_pts['base_z']

    diff[diff.z.abs() < diff_threshold]['z'] = 0.0 # Filter out small differences
    diff[diff.z.isnull()] = 0.0 # Filter out NaNs.

    diff_xyz_fname = "diff.xyz"
    diff_grid_fname = "diff.nc"
    diff.to_csv(diff_xyz_fname, sep=' ', header=False, index=False)

    os.system(f'gmt nearneighbor {diff_xyz_fname} -G{diff_grid_fname} -R{region_to_str(base_grid.region)} -I{base_grid.spacing} -S{2*max_spacing} -N4 -E0 -V')
    diff_grid, _, _ = load_source(diff_grid_fname)

    # Cleanup files
    os.remove(diff_grid_fname)
    os.remove(diff_xyz_fname)

    return diff_grid


def load_base_grid(fname, region=None, spacing=None):
    base_grid = Grid(fname, convert_to_xyz=False)
    if region:
        base_grid.crop(region)
    return base_grid

def preprocess_base_grid(base_grid, update_grid, final_spacing):
    """
    Combines and smooths data from the base and update grid,
    as described in workflow steps B+C of the GEBCO cookbook.
    This is a preprocessing step to remove-restore.
    """
    xyz1 = base_grid.as_xyz()
    xyz2 = update_grid.as_xyz()
    xyz1.append(xyz2, ignore_index=True)

    max_spacing = max(update_grid.spacing, final_spacing)
    minimal_region = min_regions(update_grid.region, base_grid.region)
    bmd = blockmedian(xyz1, spacing=4*max_spacing, region=minimal_region, Q=True)
    combined = surface(bmd.x, bmd.y, bmd.z, spacing=4*max_spacing, region=minimal_region)

    filter_combined = grdfilter(combined, D=0, F=f"c{12*max_spacing}")
    fname = "filtered.nc"
    filter_combined.to_netcdf(fname)
    combined_grid = Grid(fname)
    os.remove(fname)
    combined_grid.resample(max_spacing)

    return combined_grid

def main():
    # Handle arguments
    parser = argparse.ArgumentParser(description='Combine multiple bathymmetry sources into a single grid')
    parser.add_argument('filenames', nargs='+', help='sources to combine with the base grid')
    parser.add_argument('--base', required=True, help='base grid')
    parser.add_argument('--spacing', type=float, help='output grid spacing')
    parser.add_argument('--diff_threshold', type=float, default=0.0, help='value above which differences will be added to the base grid')
    parser.add_argument('--plot', action='store_true', help='plot final output before saving')
    parser.add_argument('--output', required=True, help='filename of final output')
    parser.add_argument('--region_of_interest', required=False, nargs=4, type=float,
                        help='output region in order <xmin> <xmax> <ymin> <ymax>. Defaults to the extent of the base grid.')
    args = parser.parse_args()

    filenames = args.filenames
    base_fname = args.base
    diff_threshold = args.diff_threshold
    output_fname = args.output
    region_of_interest = args.region_of_interest

    # Create base grid
    base_grid = load_base_grid(base_fname, region=args.region_of_interest, spacing=args.spacing)

    # Update base grid
    for fname in filenames:
        print("Loading update grid")
        update_grid = Grid(fname, convert_to_xyz=True)

        diff_grid = calc_diff_grid(base_grid, update_grid, diff_threshold=diff_threshold)

        print("Update base grid")
        base_grid.grid.values += diff_grid.values

    base_grid.save_grid(args.output)

    if args.plot:
        fig, axes = plt.subplots(2,2)
        initial_base_grid = load_base_grid(base_fname, region=args.region_of_interest)
        initial_base_grid.plot(ax=axes[0,0])
        axes[0,0].set_title("Initial Grid")
        base_grid.plot(ax=axes[0,1])
        axes[0,1].set_title("Final Grid")
        base_grid.grid.differentiate('x').plot(ax=axes[1,0])
        axes[1,0].set_title("x Derivative of Final Grid")
        base_grid.grid.differentiate('y').plot(ax=axes[1,1])
        axes[1,1].set_title("y Derivative of Final Grid")
        plt.show()

if __name__ == "__main__":
    main()
