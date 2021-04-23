import pytest
import loaders

def test_geotiff_loader():
    df = loaders.load_geotiff("./test_data/small_sample.tif")
    print(df)

def test_loader_equivalence():
    df_geotiff, _, _ = loaders.load_geotiff("./test_data/small_sample.tif")
    df_netcdf, _, _ = loaders.load_netcdf("./test_data/small_sample.nc")

    # geotiff and netcdf don't order the rows in the same way, so we sort for comparison
    # index ignored because otherwise they row index persists after sorting, and comparison doesn't work.
    sorted_geotiff = df_geotiff.sortby([df_geotiff.x, df_geotiff.y])
    sorted_netcdf = df_netcdf.sortby([df_netcdf.x, df_netcdf.y]) 

    diff_x = abs(sorted_geotiff.x - sorted_netcdf.x)
    diff_y = abs(sorted_geotiff.y - sorted_netcdf.y)
    diff_z = abs(sorted_geotiff.values - sorted_netcdf.values)
    
    assert diff_x.max() < 1.e-12
    assert diff_z.max() < 1.e-12
    assert diff_y.max() < 1.e-12
