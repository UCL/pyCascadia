#!/usr/bin/env python3

"""
Implementation of the remove-restore algorithm from the GEBCO cookbook

Note that the remove-restore algorithm consists of only "step D" described in the cookbook. Preprocessing steps A-C are not included here.
"""

from pygmt import blockmedian, surface, grdtrack, grdcut, grdfilter
import os
import pandas as pd
import matplotlib.pyplot as plt
import argparse

from pycascadia.loaders import load_source
from pycascadia.grid import Grid
from pycascadia.utility import region_to_str, min_regions, is_region_valid

def calc_diff_grid(base_grid, update_grid, diff_threshold=0.0, window_width=None):
    """Calculates difference grid for use in remove-restore"""
    print("Blockmedian update grid")
    max_spacing = max(update_grid.spacing, base_grid.spacing)
    minimal_region = min_regions(update_grid.region, base_grid.region)
    if not is_region_valid(minimal_region):
        print("Update grid is outside region of interest. Skipping.")
        return None

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

    NODATA_VAL = 9999

    os.system(f'gmt nearneighbor {diff_xyz_fname} -G{diff_grid_fname} -R{region_to_str(base_grid.region)} -I{base_grid.spacing} -S{2*max_spacing} -N4 -E{NODATA_VAL} -V')
    diff_grid, _, _ = load_source(diff_grid_fname)

    # Cleanup files
    os.remove(diff_grid_fname)
    os.remove(diff_xyz_fname)

    # Interpolate between nodata and data regions in update grid
    if window_width:
        # nodata_grid = xr.where(diff_grid == NODATA_VAL, 1.0, 0.0) # This doesn't work, for reference
        # Form grid of 0.0 where there's no data and 1.0 where there's data
        nodata_grid = diff_grid.where(diff_grid == NODATA_VAL, 1.0)
        nodata_grid = nodata_grid.where(diff_grid != NODATA_VAL, 0.0)
        # Use boxcar filter to smooth hard boundary between data & no data
        interp_grid = grdfilter(nodata_grid, filter=f'b{2*window_width}', distance=0)
        # Rescale and keep only one side of window, that on the data side
        interp_grid = (interp_grid-0.5)*2.0
        interp_grid = interp_grid.where(interp_grid > 0.0, 0.0)

        diff_grid = diff_grid.where(diff_grid != NODATA_VAL, 0.0) # Filter out nodata
        # Filter the original difference grid using the interpolation grid
        return diff_grid * interp_grid
    else:
        diff_grid = diff_grid.where(diff_grid != NODATA_VAL, 0.0) # Filter out nodata
        return diff_grid


def load_base_grid(fname, region=None, spacing=None):
    base_grid = Grid(fname, convert_to_xyz=False)
    if region:
        base_grid.crop(region)
    if spacing:
        base_grid.resample(spacing)

    return base_grid


def main():
    # Handle arguments
    parser = argparse.ArgumentParser(description='Combine multiple bathymmetry sources into a single grid')
    parser.add_argument('filenames', nargs='+', help='sources to combine with the base grid')
    parser.add_argument('--base', required=True, help='base grid')
    parser.add_argument('--spacing', type=float, help='output grid spacing')
    parser.add_argument('--diff_threshold', default=0.0, help='value above which differences will be added to the base grid')
    parser.add_argument('--plot', action='store_true', help='plot final output before saving')
    parser.add_argument('--output', required=True, help='filename of final output')
    parser.add_argument('--window_width', required=False, type=float,
                        help='Enable windowing of update grid and specify width of window in degrees')
    parser.add_argument('--region_of_interest', metavar=('xmin', 'xmax', 'ymin', 'ymax'), required=False, nargs=4, type=float,
                        help='output region. Defaults to the extent of the base grid.')
    args = parser.parse_args()

    filenames = args.filenames
    base_fname = args.base
    diff_threshold = args.diff_threshold
    output_fname = args.output
    region_of_interest = args.region_of_interest
    window_width = args.window_width

    # Create base grid
    base_grid = load_base_grid(base_fname, region=args.region_of_interest, spacing=args.spacing)

    # Update base grid
    for fname in filenames:
        print("Loading update grid")
        update_grid = Grid(fname, convert_to_xyz=True)

        diff_grid = calc_diff_grid(base_grid, update_grid,
                                   diff_threshold=diff_threshold,
                                   window_width=window_width
                                  )

        if diff_grid is not None:
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
        # diff_grid.plot(ax=axes[0,1])
        # axes[0,1].set_title("Difference Grid")
        base_grid.grid.differentiate('x').plot(ax=axes[1,0])
        axes[1,0].set_title("x Derivative of Final Grid")
        base_grid.grid.differentiate('y').plot(ax=axes[1,1])
        axes[1,1].set_title("y Derivative of Final Grid")
        plt.show()

if __name__ == "__main__":
    main()
