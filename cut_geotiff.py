"""
This is a very specific script intended to crop a geotiff file in to a small chunk for use in testing. It does keep the proper coordinate system and transform.
"""

import rasterio
from rasterio.windows import Window
import argparse

parser = argparse.ArgumentParser(description='slice geotiff file')
parser.add_argument('filename', help='input file')
parser.add_argument('--out', required=True, help='output file')
args = parser.parse_args()

filepath = args.filename
o_filepath = args.out

with rasterio.open(filepath) as src:
    window = Window.from_slices((0, 200), (0, 200))

    kwargs = src.meta.copy()
    kwargs.update({
        'height': window.height,
        'width': window.width,
        'transform': rasterio.windows.transform(window, src.transform)
    })


    with rasterio.open(o_filepath, 'w', **kwargs) as dst:
        dst.write(src.read(window=window))
