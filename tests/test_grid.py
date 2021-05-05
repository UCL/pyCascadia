import pytest
import os
from xarray.testing import assert_equal, assert_allclose

from pycascadia.grid import Grid

def test_grid_loading():
    nc_fname = './test_data/small_sample.nc'
    tif_fname = './test_data/small_sample.tif'

    grid_nc = Grid(nc_fname)
    grid_tif = Grid(tif_fname)

    assert grid_nc.spacing == grid_tif.spacing
    assert grid_nc.region == grid_tif.region

    assert_allclose(grid_nc.grid, grid_tif.grid)

def test_grid_saving():
    nc_fname = './test_data/small_sample.nc'
    nc_fname_save = './test_data/small_sample_temp.nc'

    grid_og = Grid(nc_fname)
    grid_og.save_grid(nc_fname_save)

    grid_saved = Grid(nc_fname)

    assert_equal(grid_og.grid, grid_saved.grid)

    os.remove(nc_fname_save)
