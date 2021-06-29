#!/usr/bin/env python3

"""
Implementation of the remove-restore algorithm from the GEBCO cookbook

Note that the remove-restore algorithm consists of only "step D" described in
the cookbook. Preprocessing steps A-C are not included here.
"""

from pygmt import blockmedian, grdtrack, grdfilter
from pygmt.clib import Session
from pygmt.helpers import (
    GMTTempFile,
    build_arg_string,
    kwargs_to_strings,
    use_alias,
)

import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
import argparse

from pycascadia.grid import Grid
from pycascadia.utility import min_regions, is_region_valid, \
        read_fnames, all_values_are_nodata


@use_alias(
    I="spacing",
    R="region",
    V="verbose",
)
@kwargs_to_strings(R="sequence")
def nearneighbour(data_xyz, **kwargs):
    """Uses pyGMT's clib to call GMT's nearneighbour command

    Adapted from pyGMT's [blockmedian implementation](https://github.com/GenericMappingTools/pygmt/blob/c0ff7f1add9884305688c2fa15c5f13516b8b960/pygmt/src/blockm.py)
    """
    with GMTTempFile(suffix=".csv") as tmpfile:
        with Session() as lib:
            file_context = lib.virtualfile_from_data(check_kind="vector", data=data_xyz)
            with file_context as infile:
                if "G" not in kwargs.keys():  # if outgrid is unset, output to tempfile
                    kwargs.update({"G": tmpfile.name})
                outgrid = kwargs["G"]
                arg_str = " ".join([infile, build_arg_string(kwargs)])
                lib.call_module("nearneighbor", arg_str)

        if outgrid == tmpfile.name:  # if user did not set outgrid, return DataArray
            with xr.open_dataarray(outgrid) as dataarray:
                result = dataarray.load()
                _ = result.gmt  # load GMTDataArray accessor information
        else:
            result = None  # if user sets an outgrid, return None

    return result


def create_interpolation_grid(
    diff_grid: xr.DataArray, nodata_val: int, window_width: int
) -> xr.DataArray:
    """Create filter to smooth hard edge of difference grid

    This works by creating a grid containing 1 where there is data in the input
    grid and a 0 where there is none, then applying a filter to this grid to
    smooth the boundary. This can be directly multiplied by the difference grid
    to smooth its edges.

    Args:
        diff_grid: difference grid to calculate smoothing filter from
        nodata_val: value in grid representing a lack of data
        window_width: width of smoothing region at data boundary

    Returns:
        grid which should be multiplied by input grid in order to smooth
    """
    # nodata_grid = xr.where(diff_grid == nodata_val, 1.0, 0.0) # This doesn't work, for reference

    # Form grid of 0.0 where there's no data and 1.0 where there's data
    nodata_grid = diff_grid.where(diff_grid == nodata_val, 1.0)
    nodata_grid = nodata_grid.where(diff_grid != nodata_val, 0.0)
    # Use boxcar filter to smooth hard boundary between data & no data
    interp_grid = grdfilter(nodata_grid, filter=f"b{2*window_width}", distance=0)
    # Rescale and keep only one side of window, that on the data side
    interp_grid = (interp_grid - 0.5) * 2.0
    interp_grid = interp_grid.where(interp_grid > 0.0, 0.0)

    return interp_grid


def calc_diff_grid(
    base_grid: Grid,
    update_grid: Grid,
    diff_threshold: float = 0.0,
    window_width: int = None,
) -> xr.DataArray:
    """Calculates difference grid for use in remove-restore

    Args:
        base_grid: base grid to be later updated using the calculated difference grid
        update_grid: Differences will be calculated between this and the base grid
        diff_threshold: Optional threshold above which a difference will be applied
        window_width: Width of optional smoothing window around update grid

    Returns:
        Difference grid for updating base grid
    """
    print("Blockmedian update grid")
    max_spacing = max(update_grid.spacing, base_grid.spacing)
    minimal_region = min_regions(update_grid.region, base_grid.region)
    if not is_region_valid(minimal_region):
        print("Update grid is entirely outside region of interest. Skipping.")
        return None

    if all_values_are_nodata(update_grid.grid):
        print("Update grid consists entirely of no_data_values. Skipping.")
        return None

    bmd = blockmedian(update_grid.xyz,
                      spacing=max_spacing,
                      region=minimal_region)

    print("Find z in base grid")
    base_pts = grdtrack(bmd, base_grid.grid, "base_z", interpolation="l")

    print("Create difference grid")
    diff = pd.DataFrame()
    diff["x"] = base_pts["x"]
    diff["y"] = base_pts["y"]
    diff["z"] = base_pts["z"] - base_pts["base_z"]

    diff[diff.z.abs() < diff_threshold]["z"] = 0.0  # Filter out small differences

    NODATA_VAL = 9999

    diff_grid = nearneighbour(diff,
                              region=base_grid.region,
                              spacing=base_grid.spacing,
                              S=2*max_spacing, N=4, E=NODATA_VAL,
                              verbose=True)

    # Interpolate between nodata and data regions in update grid
    if window_width:
        interp_grid = create_interpolation_grid(
            diff_grid, NODATA_VAL, window_width)

        # Filter out nodata
        diff_grid = diff_grid.where(diff_grid != NODATA_VAL, 0.0)
        # Filter the original difference grid using the interpolation grid
        diff_grid = diff_grid * interp_grid
    else:
        # Filter out nodata
        diff_grid = diff_grid.where(diff_grid != NODATA_VAL, 0.0)

    return diff_grid


def load_base_grid(fname: str, region: list = None, spacing: bool = None) -> Grid:
    """Load base grid from file optionally cropping and resampling

    Args:
        fname: filename of input grid
        region: Optional region to crop to
        spacing: Optional grid spacing to which the base grid will be resampled

    Returns:
        Grid containing base grid
    """
    base_grid = Grid(fname, convert_to_xyz=False)
    if region:
        base_grid.crop(region)
    if spacing:
        base_grid.resample(spacing)

    return base_grid


def main():
    """Main entry point for remove-restore command line tool

    This handles arguments, applies the remove-restore algorithm then, optionally, plots the results.
    """
    # Handle arguments
    parser = argparse.ArgumentParser(description='Combine multiple bathymmetry sources into a single grid')
    parser.add_argument('filenames', nargs='*', help='sources to combine with the base grid')
    parser.add_argument('--base', required=True, help='base grid')
    parser.add_argument('--input_txt', help='text file containing list of input grids')
    parser.add_argument('--spacing', type=float, help='output grid spacing')
    parser.add_argument('--diff_threshold', default=0.0, help='value above which differences will be added to the base grid')
    parser.add_argument('--plot', action='store_true', help='plot final output before saving')
    parser.add_argument('--output', required=True, help='filename of final output')
    parser.add_argument('--window_width', required=False, type=float,
                        help='Enable windowing of update grid and specify width of window in degrees')
    parser.add_argument('--region_of_interest', metavar=('xmin', 'xmax', 'ymin', 'ymax'), required=False, nargs=4, type=float,
                        help='output region. Defaults to the extent of the base grid.')
    args = parser.parse_args()

    filenames = []
    if args.input_txt:
        # Read filenames from file
        filenames += read_fnames(args.input_txt)
    # Add filenames from command line
    filenames += args.filenames

    assert filenames != [], "No filenames given"

    base_fname = args.base
    diff_threshold = args.diff_threshold
    output_fname = args.output
    region_of_interest = args.region_of_interest
    window_width = args.window_width

    # Create base grid
    base_grid = load_base_grid(
        base_fname, region=region_of_interest, spacing=args.spacing
    )

    # Update base grid
    for fname in filenames:
        print("Loading update grid")
        update_grid = Grid(fname, convert_to_xyz=True)

        diff_grid = calc_diff_grid(
            base_grid,
            update_grid,
            diff_threshold=diff_threshold,
            window_width=window_width,
        )

        if diff_grid is not None:
            print("Update base grid")
            base_grid.grid.values += diff_grid.values

    base_grid.save_grid(output_fname)

    if args.plot:
        fig, axes = plt.subplots(2, 2)
        initial_base_grid = load_base_grid(base_fname, region=region_of_interest)
        initial_base_grid.plot(ax=axes[0, 0])
        axes[0, 0].set_title("Initial Grid")
        base_grid.plot(ax=axes[0, 1])
        axes[0, 1].set_title("Final Grid")
        # diff_grid.plot(ax=axes[0,1])
        # axes[0,1].set_title("Difference Grid")
        base_grid.grid.differentiate("x").plot(ax=axes[1, 0])
        axes[1, 0].set_title("x Derivative of Final Grid")
        base_grid.grid.differentiate("y").plot(ax=axes[1, 1])
        axes[1, 1].set_title("y Derivative of Final Grid")
        plt.show()


if __name__ == "__main__":
    main()
