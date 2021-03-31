import pytest
import loaders

def test_geotiff_loader():
    df = loaders.load_geotiff("./test_data/small_sample.tif")
    print(df)

def test_loader_equivalence():
    df_geotiff, _ = loaders.load_geotiff("./test_data/small_sample.tif")
    df_netcdf = loaders.load_netcdf("./test_data/small_sample.nc", convert_to_xyz=True)

    # geotiff and netcdf don't order the rows in the same way, so we sort for comparison
    # index ignored because otherwise they row index persists after sorting, and comparison doesn't work.
    sorted_geotiff = df_geotiff.sort_values(["x", "y"], ignore_index=True)
    sorted_netcdf = df_netcdf.sort_values(["x", "y"], ignore_index=True)

    import matplotlib.pyplot as plt
    diff_x = abs(sorted_geotiff.x - sorted_netcdf.x)
    plt.plot(diff_x)
    plt.show()
    assert diff_x.max() < 1.e-12

    diff_y = abs(sorted_geotiff.y - sorted_netcdf.y)
    plt.plot(diff_y)
    plt.show()
    assert diff_y.max() < 1.e-12
    
    # TODO these don't pass! Why? Is the meshgridding in load_geotiff correct?
    # assert sorted_geotiff.x.all == sorted_netcdf.x.all
    # assert sorted_geotiff.y.all == sorted_netcdf.y.all