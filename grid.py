"""
Grid class representing a grid of data either in xarray format or in pandas dataframe format
"""

from pygmt import grdcut
from loaders import load_source, xr_to_xyz, filter_nodata, extract_region

class Grid:
    def __init__(self, fname, convert_to_xyz=False):
        self.load(fname)

        if convert_to_xyz:
            self.xyz = self.as_xyz()

    def load(self, fname):
        """Loads data from file"""
        self.grid, self.region, self.spacing = load_source(fname)

    def crop(self, region):
        """Crops grid using grdcut"""
        if region == self.region:
            return

        self.grid = grdcut(self.grid, region=region)
        self.region = extract_region(self.grid)

    def as_xyz(self):
        """Returns pandas dataframe representation"""
        xyz_data = xr_to_xyz(self.grid)
        if hasattr(self.grid, 'nodatavals'):
            filter_nodata(xyz_data, self.grid.nodatavals)
        return xyz_data

    def plot(self, ax=None):
        """Plots data (useful for testing)"""
        self.grid.plot(ax=ax)

    def save_grid(self, fname):
        """Saves grid to netcdf file"""
        self.grid.to_netcdf(fname)
