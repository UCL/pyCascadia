#!/usr/bin/env python3

from pycascadia.loaders import load_source
import matplotlib.pyplot as plt
import argparse

def replace_land_with_zeros(arr, test_arr=None):
    if test_arr is None:
        test_arr = arr

    arr[test_arr>0] = 0


def main():
    # Handle arguments
    parser = argparse.ArgumentParser(description='Add halo surrounding given netcdf file')
    parser.add_argument('--input', required=True, help='input file')
    parser.add_argument('--output', required=True, help='output file')
    parser.add_argument('--offset', action='store_true', default=False, help='use one index from true boundary as boundary')
    parser.add_argument('--plot', action='store_true', default=False, help='plot final grid before saving')
    args = parser.parse_args()

    in_fname = args.input
    input_grid, _, _  = load_source(in_fname, plot=False)

    if args.offset:
        replace_land_with_zeros(input_grid[0,:], input_grid[1,:])
        replace_land_with_zeros(input_grid[-1,:], input_grid[-2,:])
        replace_land_with_zeros(input_grid[:,0], input_grid[:,1])
        replace_land_with_zeros(input_grid[:,-1], input_grid[:,-2])
    else:
        replace_land_with_zeros(input_grid[0,:])
        replace_land_with_zeros(input_grid[-1,:])
        replace_land_with_zeros(input_grid[:,0])
        replace_land_with_zeros(input_grid[:,-1])

    if args.plot:
        # Plot bath & contour on top
        input_grid.plot()
        plt.contour(input_grid.x, input_grid.y, input_grid.values, levels=[0.0])

        # Increase view of region to display closed contours
        BORDER_SCALE = 0.1
        x_diff = input_grid.x[-1] - input_grid.x[0]
        y_diff = input_grid.y[-1] - input_grid.y[0]
        plt.xlim(input_grid.x[0]-BORDER_SCALE*x_diff, input_grid.x[-1]+BORDER_SCALE*x_diff)
        plt.ylim(input_grid.y[0]-BORDER_SCALE*y_diff, input_grid.y[-1]+BORDER_SCALE*y_diff)

        plt.show()

    input_grid.to_netcdf(args.output)

if __name__ == "__main__":
    main()
