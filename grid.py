"""
Grid class representing a grid of data either in xarray format or in pandas dataframe format
"""

from loaders import load_source

class Grid:
    def __init__(self, fname, convert_to_xyz=False):
        self.grid, self.region, self.spacing = load_source(
            fname, convert_to_xyz=convert_to_xyz
        )


