#!/usr/bin/env python3

from pycascadia.loaders import load_source
from pygmt import grdcut
import matplotlib.pyplot as plt
import argparse


def clip_to_value(arr, test_arr=None, value=0.0):
    if test_arr is None:
        test_arr = arr

    arr[test_arr > value] = value


def main():
    # Handle arguments
    parser = argparse.ArgumentParser(
        description="Add halo surrounding given netcdf file"
    )
    parser.add_argument("--input", required=True, help="input file")
    parser.add_argument("--output", required=True, help="output file")
    parser.add_argument(
        "--value", type=float, default=0.0, help="value to replace boundary with"
    )
    parser.add_argument(
        "--offset",
        action="store_true",
        default=False,
        help="use one index from true boundary as boundary",
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        default=False,
        help="plot final grid before saving",
    )
    parser.add_argument(
        "--region",
        required=False,
        metavar=("xmin", "xmax", "ymin", "ymax"),
        nargs=4,
        type=float,
        help="output region. Defaults to the extent of the input grid.",
    )
    args = parser.parse_args()

    in_fname = args.input
    input_grid, _, _ = load_source(in_fname, plot=False)

    if args.region:
        input_grid = grdcut(input_grid, region=args.region)

    if args.offset:
        clip_to_value(input_grid[0, :], input_grid[1, :], value=args.value)
        clip_to_value(input_grid[-1, :], input_grid[-2, :], value=args.value)
        clip_to_value(input_grid[:, 0], input_grid[:, 1], value=args.value)
        clip_to_value(input_grid[:, -1], input_grid[:, -2], value=args.value)
    else:
        clip_to_value(input_grid[0, :], value=args.value)
        clip_to_value(input_grid[-1, :], value=args.value)
        clip_to_value(input_grid[:, 0], value=args.value)
        clip_to_value(input_grid[:, -1], value=args.value)

    if args.plot:
        # Plot bath & contour on top
        input_grid.plot()
        plt.contour(input_grid.x, input_grid.y, input_grid.values, levels=[args.value], colors=['green'])

        # Increase view of region to display closed contours
        BORDER_SCALE = 0.1
        x_diff = input_grid.x[-1] - input_grid.x[0]
        y_diff = input_grid.y[-1] - input_grid.y[0]
        plt.xlim(
            input_grid.x[0] - BORDER_SCALE * x_diff,
            input_grid.x[-1] + BORDER_SCALE * x_diff,
        )
        plt.ylim(
            input_grid.y[0] - BORDER_SCALE * y_diff,
            input_grid.y[-1] + BORDER_SCALE * y_diff,
        )

        plt.show()

    input_grid.to_netcdf(args.output)


if __name__ == "__main__":
    main()
