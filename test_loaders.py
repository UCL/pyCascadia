import pytest
import loaders

def test_geotiff_loader():
    df = loaders.load_geotiff("./test_data/small_sample.tif")
    print(df)

def test_loader_equivalence():
    df_geotiff = loaders.load_geotiff("./test_data/small_sample.tif")
    df_netcdf = loaders.load_netcdf("./test_data/small_sample.nc")

    # geotiff and netcdf don't order the rows in the same way, so we sort for comparison
    # index ignored because otherwise they row index persists after sorting, and comparison doesn't work.
    sorted_geotiff = df_geotiff.sort_values(["x", "y"], ignore_index=True)
    sorted_netcdf = df_netcdf.sort_values(["x", "y"], ignore_index=True)

    diff_x = abs(sorted_geotiff.x - sorted_netcdf.x)
    diff_y = abs(sorted_geotiff.y - sorted_netcdf.y)
    diff_z = abs(sorted_geotiff.z - sorted_netcdf.z)
    
    assert diff_x.max() < 1.e-12
    assert diff_z.max() < 1.e-12
    assert diff_y.max() < 1.e-12
