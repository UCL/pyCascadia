import pytest
import os
import pandas as pd
from xarray.testing import assert_equal

from pycascadia.remove_restore import nearneighbour
from pycascadia.utility import region_to_str
from pycascadia.loaders import load_source


def test_nearneighbour():
    region = [0, 1, 0, 1]
    spacing = 0.3
    NODATA_VAL = 9999
    max_spacing = 0.2

    data_xyz = pd.DataFrame.from_dict(
        {
            "x": [0.1, 0.4, 0.7],
            "y": [0.2, 0.3, 0.4],
            "z": [10, 14, 4],
        }
    )

    # Create grid via nearneighbour function
    clib_grid = nearneighbour(
        data_xyz,
        region=region,
        spacing=spacing,
        S=2 * max_spacing,
        N=4,
        E=NODATA_VAL,
        verbose=True,
    )

    # Create grid via manual os call to gmt
    data_xyz_fname = "data.xyz"
    data_grid_fname = "data.nc"
    data_xyz.to_csv(data_xyz_fname, sep=" ", header=False, index=False)
    os.system(
        f"gmt nearneighbor {data_xyz_fname} -G{data_grid_fname} -R{region_to_str(region)} -I{spacing} -S{2*max_spacing} -N4 -E{NODATA_VAL} -V"
    )
    manual_grid, _, _ = load_source(data_grid_fname)
    os.remove(data_grid_fname)
    os.remove(data_xyz_fname)

    assert_equal(manual_grid, clib_grid)
