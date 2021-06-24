import pytest

from pycascadia.utility import is_region_valid

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
