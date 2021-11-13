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
# # Day 13 : Data challenge 2: Natural Earth
#
# Great public domain map dataset for cartography on global and national scales.
# Get it at https://github.com/nvkelso/natural-earth-vector/tree/master/geojson
# or https://www.naturalearthdata.com.

# %%
import os
import zipfile

import pygmt

# %% [markdown]
# ## Download Natural Earth 1:50m Cross-blended Hypsometric Tints
#
# Shaded relief combined with custom elevation colors based on climate —
# humid lowlands are green and arid lowlands brown. Data link is at
# https://www.naturalearthdata.com/downloads/50m-raster-data/50m-cross-blend-hypso
#
# Note: The website says v3.2.0, but after downloading,
# the *.VERSION.txt says v2.0.0, just so you know.

# %%
# Download and unzip Natural Earth Cross-blended Hypsometric Tint
# with Shaded Relief and Water GeoTiff file
pygmt.which(
    fname="https://naturalearth.s3.amazonaws.com/50m_raster/HYP_50M_SR_W.zip",
    download=True,
)
with zipfile.ZipFile(file="HYP_50M_SR_W.zip") as z:
    for zip_info in z.infolist():
        z.extract(member=zip_info)

# %%
# Inspect the GeoTIFF file's metadata
print(pygmt.grdinfo(grid="HYP_50M_SR_W.tif"))

# %% [markdown]
# ## Plot the map!
#
# Let's plot the Oceania region on an
# [Orthographic Projection](https://www.pygmt.org/v0.5.0/projections/azim/azim_orthographic.html)
# using PyGMT's [`grdimage`](https://www.pygmt.org/v0.5.0/api/generated/pygmt.Figure.grdimage.html).
# There will be two layers to this, from bottom to top:
#
# 1. Hillshaded bathymetry from SRTM15+V2.1, clipped to water regions only
# 2. The Natural Earth Hypsometric Tint layer with a bit of transparency

# %%
fig = pygmt.Figure()

# Orthographic projection centred at 160E/20S
with pygmt.config(MAP_FRAME_PEN="thinnest,black"):
    fig.basemap(projection="G160/-20/12c", region="d", frame="WSNE+gwhite")

# Plot hillshaded bathymetry (areas in water)
fig.coast(resolution="c", water=True)  # start water clip path
fig.grdimage(grid="@earth_relief_10m", cmap="bukavu", shading=True)
fig.coast(Q=True)  # end water clip path

# Natural Earth Hypsometric Tint layer
fig.grdimage(grid="HYP_50M_SR_W.tif", dpi=300, transparency=25)

fig.savefig(fname="day13_natural_earth.png", transparent=True)
fig.show()
