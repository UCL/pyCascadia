"""
Misc utility functions
"""

import xarray as xr
import pandas


def region_to_str(region: list) -> str:
    """Convert region list to string format suitable for GMT.

    Args:
        region: Bounding box in format [xmin, xmax, ymin, ymax].

    Returns:
        Region in string format suitable for GMT.
    """
    return "/".join(map(str, region))


def min_regions(region1: list, region2: list) -> list:
    """Calculates the intersection of the two regions.

    Args:
        region1: First region.
        region2: Second region.

    Returns:
        Region representing the intersection of two input regions.
    """
    return [
        max(region1[0], region2[0]),
        min(region1[1], region2[1]),
        max(region1[2], region2[2]),
        min(region1[3], region2[3]),
    ]


def is_region_valid(region: list) -> bool:
    """Determines if input region is a valid region, that is its right hand
    side is to the right of its left, and similar for the upper and lower sides.

    Args:
        region: Input region.

    Returns:
        True if region valid, False otherwise.
    """
    if region[1] < region[0] or region[3] < region[2]:
        return False
    else:
        return True


def all_values_are_nodata(grid: xr.DataArray) -> bool:
    """Determines if all values in grid are nodata

    Args:
        grid: Xarray grid.

    Returns:
        True if all values in grid are nodata values, False otherwise.
    """
    return (grid.nodatavals == grid.values).all()


def read_fnames(input_txt: str) -> list:
    """Reads filenames from text file, removing empty lines
    and training newlines.

    Args:
        input_txt: File from which filenames will be read.

    Returns:
        List of filenames.
    """
    with open(input_txt, "r") as fp:
        lines = [fname.strip() for fname in fp.readlines() if fname != "\n"]

    return lines


def xr_to_xyz(xr_data: xr.DataArray) -> pandas.DataFrame:
    """Converts an xarray dataarray into a pandas dataframe.

    This requires the input coordinates to be named (x,y) and the
    elevation to be named z.

    Args:
        xr_data: Xarray grid.

    Returns:
        Pandas dataframe of xyz points.
    """
    xyz_data = xr_data.to_dataframe()
    xyz_data = xyz_data.reset_index()
    xyz_data = xyz_data[["x", "y", "z"]]
    return xyz_data


def filter_nodata(xyz_data: pandas.DataFrame, nodatavals: list) -> None:
    """Removes values in nodatavals from input.

    Args:
        xyz_data: Dataframe of points to filter.
        nodatavals: List of values to remove from xyz_data.
    """
    for nodata_val in nodatavals:
        xyz_data.where(xyz_data["z"] != nodata_val, inplace=True)


def delete_variable(ds: xr.Dataset, varname: str) -> None:
    """
    Remove variable from xarray dataset.

    Args:
        ds: Dataset from which the variable will be removed.
        varname: Name of variable to be removed.
    """
    if varname in ds:
        del ds[varname]
    else:
        raise ValueError(f"Could not find {varname} in dataset")
