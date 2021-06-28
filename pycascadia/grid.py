"""
Grid class representing a grid of data either in xarray format or in pandas dataframe format
"""

import os
from pygmt import grdcut

from pycascadia.loaders import load_source, extract_region
from pycascadia.utility import region_to_str, xr_to_xyz, filter_nodata

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

    def resample(self, spacing):
        """Resamples the loaded grid using gdal's grdsample"""
        if spacing == self.spacing:
            return

        print(f'Resampling from {self.spacing} to {spacing}')
        in_fname = 'original.nc'
        self.save_grid(in_fname)
        out_fname = 'resampled.nc'
        os.system(f'gmt grdsample {in_fname} -G{out_fname} -R{region_to_str(self.region)} -I{spacing} -V')
        self.load(out_fname)
        os.remove(in_fname)
        os.remove(out_fname)

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
