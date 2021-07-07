import pytest

from pycascadia.utility import is_region_valid, read_fnames

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

def test_read_fnames():
    in_fnames = read_fnames('test_data/filenames.txt')
    true_fnames = ['test1', 'test2', 'filename3.txt', 'ncfile.nc']

    for in_fname, true_fname in zip(in_fnames, true_fnames):
        assert in_fname == true_fname
