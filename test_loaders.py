import pytest
import loaders

def test_geotiff_loader():
    df = loaders.load_geotiff("./test_data/small_sample.tif")
    print(df)
