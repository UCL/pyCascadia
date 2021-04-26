import pytest
import loaders
from xarray.testing import assert_equal, assert_allclose

def test_loader_equivalence():
    xr_geotiff, _, _ = loaders.load_source("./test_data/small_sample.tif")
    xr_netcdf, _, _ = loaders.load_source("./test_data/small_sample.nc")

    assert_allclose(xr_geotiff, xr_netcdf)
