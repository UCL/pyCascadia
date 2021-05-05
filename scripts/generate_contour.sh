#!/usr/bin/env bash

export GRASS_MESSAGE_FORMAT=plain

input_fname=$1
output_fname=$2

r.in.gdal input=NETCDF:"$input_fname" output=elevation -o --overwrite
r.contour in=elevation out=contours levels=0 cut=200 --overwrite
v.out.ogr format=ESRI_Shapefile input=contours output=$output_fname --overwrite

# For plotting
#g.region raster=elevation
#d.mon start=png
#d.rast elevation
#d.vect contours color=red
