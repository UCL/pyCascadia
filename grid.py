"""
Grid class representing a grid of data either in xarray format or in pandas dataframe format
"""

from loaders import load_source, xr_to_xyz, filter_nodata

class Grid:
    def __init__(self, fname, convert_to_xyz=False):
        self.grid, self.region, self.spacing = load_source(fname)
        if convert_to_xyz:
            self.xyz = self.as_xyz()

    def grdcut(self, region):
        """Crops grid using grdcut"""
        self.grid = grdcut(self.grid, region=region)
        self.region = region

    def as_xyz(self):
        """Returns pandas dataframe representation"""
        xyz_data = xr_to_xyz(self.grid)
        if hasattr(self.grid, 'nodatavals'):
            filter_nodata(xyz_data, self.grid.nodatavals)
        return xyz_data

    def plot(self, ax=None):
        self.grid.plot(ax=ax)

    def save_grid(self, fname):
        self.grid.to_netcdf(fname)
