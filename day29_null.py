# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:hydrogen
#     text_representation:
#       extension: .py
#       format_name: hydrogen
#       format_version: '1.3'
#       jupytext_version: 1.9.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Day 29 : NULL
#
# `   `

# %%
import os
import zipfile

import fiona
import geopandas as gpd
import pygmt

# %% [markdown]
# ## Download Reference Elevation Model of Antarctica
#
# This is a Digital Elevation Model (DEM) of Antarctica.
# Specifically, we'll get the 1km spatial resolution, v1.1,
# non gap-filled version from https://www.pgc.umn.edu/data/rema
#
# References:
# - Howat, I. M., Porter, C., Smith, B. E., Noh, M.-J., & Morin, P. (2019). The Reference Elevation Model of Antarctica. The Cryosphere, 13(2), 665–674. https://doi.org/10.5194/tc-13-665-2019

# %%
# Download REMA unfilled DEM
pygmt.which(fname="https://data.pgc.umn.edu/elev/dem/setsm/REMA/mosaic/v1.1/1km/REMA_1km_dem.tif", download=True)

# %%
# Inspect the GeoTIFF file's metadata
print(pygmt.grdinfo(grid="REMA_1km_dem.tif"))

# %% [markdown]
# ## Download ICESat-2 reference ground tracks
#
# These are ICESat-2's orbital ground tracks over Antarctica,
# which go up to 88°S. Obtained from https://icesat-2.gsfc.nasa.gov/science/specs

# %%
# https://gis.stackexchange.com/questions/114066/handling-kml-csv-with-geopandas-drivererror-unsupported-driver-ucsv/258370#258370
fiona.drvsupport.supported_drivers['LIBKML'] = 'rw' # enable KML support which is disabled by default

# %%
# Download and unzip KMZ file
pygmt.which(fname="https://icesat-2.gsfc.nasa.gov/sites/default/files/page_files/antarcticaallorbits.zip", download=True)
with zipfile.ZipFile(file="antarcticaallorbits.zip") as z:
    for zip_info in z.infolist():
        if zip_info.filename.endswith("Antarctica_repeat1_GT7.kmz"):
            zip_info.filename = os.path.basename(zip_info.filename)
            z.extract(member=zip_info)

# %%
gdf: gpd.GeoDataFrame = gpd.read_file("Antarctica_repeat1_GT7.kmz")
gdf

# %% [markdown]
# ## Plot the map!
#
# First we'll plot the REMA DEM using
# [`fig.grdimage`](https://www.pygmt.org/v0.5.0/api/generated/pygmt.Figure.grdimage.html).
# Next, the ICESat-2 track lines are plotted using
# [`fig.plot`](https://www.pygmt.org/v0.5.0/api/generated/pygmt.Figure.plot.html).
# The projection needs to be set to an Antarctic Polar Stereographic projection
# (EPSG:3031), and be of the same map scale and region as the REMA DEM.
# There are some additional configurations used (see
# https://docs.generic-mapping-tools.org/6.2/gmt.conf.html)
# to make the graticule lines look nicer.

# %%
fig = pygmt.Figure()

with pygmt.config(
    MAP_FRAME_TYPE="inside",
    MAP_ANNOT_OBLIQUE=0,
    v="88/90",  # less longitude graticules at >88°S
):
    # Plot REMA DEM
    fig.grdimage(
        grid="REMA_1km_dem.tif",
        projection="x1:30000000",
        cmap="fes",
        nan_transparent=True,
    )
    # Plot ICESat-2 tracks
    fig.plot(
        data=gdf,  # SRTM15+V2.1
        pen="0.001p,green",
        # Antarctic Polar Stereographic projection
        projection="s0/-90/-71/1:30000000",  # slon0/lat0[/horizon]/scale
        region="REMA_1km_dem.tif",
        frame=["NSWE", "xa45g45", "ya10g10"],
    )

fig.savefig(fname="day29_null.png")
fig.show()
