import pytest

import xarray as xr
from pycascadia.utility import is_region_valid, all_values_are_nodata, read_fnames, delete_variable

def test_is_region_valid():
    # Maximum > minimum in each direction
    valid_region = [100, 200, 300, 400]
    assert is_region_valid(valid_region) == True

    # min x > max x
    invalid_region_x = [200, 100, 300, 400]
    assert is_region_valid(invalid_region_x) == False

    # min y > max y
    invalid_region_y = [100, 200, 400, 300]
    assert is_region_valid(invalid_region_y) == False

def test_all_values_are_nodata():
    nodata_grid = xr.DataArray([9999,9999,9999,9999])
    nodata_grid.attrs['nodatavals'] = 7777
    assert all_values_are_nodata(nodata_grid) == False
    nodata_grid.attrs['nodatavals'] = 9999
    assert all_values_are_nodata(nodata_grid) == True

def test_read_fnames():
    in_fnames = read_fnames('test_data/filenames.txt')
    true_fnames = ['test1', 'test2', 'filename3.txt', 'ncfile.nc']

    for in_fname, true_fname in zip(in_fnames, true_fnames):
        assert in_fname == true_fname

def test_delete_variable():
    fname = './test_data/contains_extra_var.nc'
    ds = xr.load_dataset(fname)

    # Ensure ds initially contains the variable
    assert 'crs' in ds

    # Ensure deleting works
    delete_variable(ds, 'crs')
    assert 'crs' not in ds

    # Ensure deleting a missing variable throws
    with pytest.raises(ValueError, match=f"Could not find crs in dataset"):
        delete_variable(ds, 'crs')
