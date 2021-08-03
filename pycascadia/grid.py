"""Grid contains a grid of data in xarray format"""

import os
import pandas
from pygmt import grdcut

from pycascadia.loaders import load_source, extract_region
from pycascadia.utility import region_to_str, xr_to_xyz, filter_nodata


class Grid:
    """Grid contains a grid of data in xarray format and optionally as xyz points in pandas dataframe format.

    Grids are intended to be initially loaded from file and can be further manipulated in the following ways:

    - resampling to a different grid spacing
    - cropping to a given region
    - conversion to a list of xyz datapoints.
    - saved to file

    Coordinates will be labelled `x` and `y`, and (depth/elevation) values will be labelled `z`.

    The internal grid may also be manipulated and is exposed through Grid.grid or Grid.xyz (if the grid has already been converted).
    """

    def __init__(self, fname: str, convert_to_xyz: bool = False) -> None:
        """
        Constructor

        Args:
            fname: Input grid filename.
            convert_to_xyz: Whether the grid should be converted to xyz points.
        """
        self.load(fname)

        if convert_to_xyz:
            self.xyz = self.as_xyz()

    def load(self, fname: str) -> None:
        """
        Loads data from file. See loaders for supported file formats.

        Args:
            fname: Input grid filename.
        """
        self.grid, self.region, self.spacing = load_source(fname)

    def crop(self, region: list) -> None:
        """
        Crops grid using grdcut.

        Args:
            region: Bounding box of region to crop to (in format [xmin, xmax, ymin, ymax]).
        """
        if region == self.region:
            return

        self.grid = grdcut(self.grid, region=region)
        self.region = extract_region(self.grid)

    def resample(self, spacing: float) -> None:
        """
        Resamples the loaded grid using gdal's grdsample.

        Args:
            spacing: Grid spacing of resampled grid.
        """
        if spacing == self.spacing:
            return

        print(f"Resampling from {self.spacing} to {spacing}")
        in_fname = "original.nc"
        self.save_grid(in_fname)
        out_fname = "resampled.nc"
        os.system(
            f"gmt grdsample {in_fname} -G{out_fname} -R{region_to_str(self.region)} -I{spacing} -V"
        )
        self.load(out_fname)
        os.remove(in_fname)
        os.remove(out_fname)

    def as_xyz(self) -> pandas.DataFrame:
        """
        Returns pandas dataframe representation.
        """
        xyz_data = xr_to_xyz(self.grid)
        if hasattr(self.grid, "nodatavals"):
            filter_nodata(xyz_data, self.grid.nodatavals)
        return xyz_data

    def plot(self, ax=None) -> None:
        """
        Plots data (useful for testing).

        Args:
            ax: Axis used for plotting (will be created if not supplied).
        """
        self.grid.plot(ax=ax)

    def save_grid(self, fname: str) -> None:
        """
        Saves grid to netcdf file.

        Args:
            fname: Output filename.
        """
        self.grid.to_netcdf(fname)
