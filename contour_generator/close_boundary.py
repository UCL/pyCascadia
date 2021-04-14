#!/usr/bin/env python3

from loaders import load_source
import argparse

def replace_with_zeros(arr, test_arr=None):
    if test_arr is None:
        test_arr = arr

    arr[test_arr>0] = 0


def main():
    # Handle arguments
    parser = argparse.ArgumentParser(description='Add halo surrounding given netcdf file')
    parser.add_argument('--input', required=True, help='input file')
    parser.add_argument('--output', required=True, help='output file')
    parser.add_argument('--inplace', action='store_true', default=True, help='replace boundary values')
    parser.add_argument('--offset', action='store_true', default=False, help='use one index from true boundary as boundary')
    args = parser.parse_args()

    in_fname = args.input
    input_grid = load_source(in_fname, plot=False)

    if args.inplace:
        if args.offset:
            replace_with_zeros(input_grid[0,:], input_grid[1,:])
            replace_with_zeros(input_grid[-1,:], input_grid[-2,:])
            replace_with_zeros(input_grid[:,0], input_grid[:,1])
            replace_with_zeros(input_grid[:,-1], input_grid[:,-2])
        else:
            replace_with_zeros(input_grid[0,:])
            replace_with_zeros(input_grid[-1,:])
            replace_with_zeros(input_grid[:,0])
            replace_with_zeros(input_grid[:,-1])
    else:
        raise NotImplementedError("Adding an additionl halo is not supported yet")

    input_grid.to_netcdf(args.output)

if __name__ == "__main__":
    main()
