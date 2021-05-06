import pytest
from xarray.testing import assert_equal, assert_allclose

from pycascadia.loaders import load_source

def test_loader_equivalence():
    xr_geotiff, _, _ = load_source("./test_data/small_sample.tif")
    xr_netcdf, _, _ = load_source("./test_data/small_sample.nc")

    assert_allclose(xr_geotiff, xr_netcdf)
