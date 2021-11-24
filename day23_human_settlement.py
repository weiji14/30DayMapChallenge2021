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
# # Day 23 : Data challenge 3: Global Human Settlement Layer
#
# The third data challenge should be created using this great dataset by EC JRC
# on human population. You can find it [here](https://ghsl.jrc.ec.europa.eu/).
# Different resolutions and areas you can choose from.

# %%
import pandas as pd
import pygmt
import rioxarray
import xarray as xr

# %% [markdown]
# ## Download and preprocess GHS-BUILT-S2 R2020A for NW Borneo
#
# GHS-BUILT-S2 R2020A is a built-up grid derived from Sentinel-2
# global image composite for reference year 2018
# using Convolutional Neural Networks (GHS-S2Net).
# Tiles can be downloaded from https://ghsl.jrc.ec.europa.eu/download.php?ds=buS2
#
# This dataset corresponds to global map of built-up areas expressed
# in terms of a probability grid at 10 m spatial resolution derived
# from a Sentinel-2 global image composite
# (GHS_composite_S2_L1C_2017-2018_GLOBE_R2020A_UTM_10_v1_0)
# for reference year 2018.
# It builds on a new Deep Learning framework for pixel-wise large-scale
# classification of built-up areas named GHS-S2Net (GHS stands for
# Global Human Settlements, S2 refers to the Sentinel-2 satellite).
#
# Dataset:
# - Corbane, Christina; Sabo, Filip; Politis, Panagiotis; Syrris Vasileos (2020): GHS-BUILT-S2 R2020A - built-up grid derived from Sentinel-2 global image composite for reference year 2018 using Convolutional Neural Networks (GHS-S2Net). European Commission, Joint Research Centre (JRC) PID: http://data.europa.eu/89h/016d1a34-b184-42dc-b586-e10b915dd863, doi:10.2905/016D1A34-B184-42DC-B586-E10B915DD863
#
# Concept & Methodology:
# - Corbane, C., Syrris, V., Sabo, F. et al. Convolutional neural networks for global human settlements mapping from Sentinel-2 satellite imagery. Neural Comput & Applic (2020). doi:10.1007/s00521-020-05449-7

# %%
ghs_50n: xr.DataArray = rioxarray.open_rasterio(
    filename="https://cidportal.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/GHS_BUILT_S2comp2018_GLOBE_R2020A/GHS_BUILT_S2comp2018_GLOBE_R2020A_UTM_10/V1-0/50N_PROB.tif",
    # masked=True,
    # overview_level=1,
)

# %%
# Clip to bounding box of Bandar Seri Begawan (EPSG:32650/UTM zone 50N coordinates)
ghs_bsb: xr.DataArray = ghs_50n.rio.clip_box(
    minx=260_000, maxx=300_000, miny=520_000, maxy=560_000
)

# %%
# Save clipped grid to a GeoTIFF file
ghs_bsb.rio.to_raster(raster_path="ghs_bsb.tif", dtype="uint16")

# %%
# Inspect the metadata of the GeoTIFF file
print(pygmt.grdinfo(grid="ghs_bsb.tif"))

# %% [markdown]
# ## Plot the map!
#
# Time to map this up! We'll use PyGMT's
# [`grdimage`](https://www.pygmt.org/v0.5.0/api/generated/pygmt.Figure.grdimage.html)
# to lay down the Sentinel 3 imagery, and plot the ICESat-2 derived grounding
# points symbolized based on their type (H, I, F).
#
# 3D histogram example based on
# https://docs.generic-mapping-tools.org/6.2/gallery/ex08.html
#
# Note: there's some tricks to mixing UTM and Geographic datasets in one plot,
# refer to https://docs.generic-mapping-tools.org/6.2/gallery/ex28.html

# %%
# Convert raster grid cells to XYZ table
df_: pd.DataFrame = pygmt.grd2xyz(grid="ghs_bsb.tif", nodata=0, skiprows=True)

# %%
# Block average points to 50mx50m cells
df: pd.DataFrame = pygmt.blockmean(
    data=df_, spacing="50+e", region=[260_000, 300_000, 520_000, 560_000]
)
df.describe()

# %%
fig = pygmt.Figure()

# Plot 3D histogram of built settlement probability
with pygmt.config(PS_PAGE_COLOR="black"):
    pygmt.makecpt(cmap="batlowK", series=(0, 75, 5))
    fig.plot3d(
        data=df[["x", "y", "z", "z"]],
        region=[260_000, 300_000, 520_000, 560_000, 0, 100],
        projection="x1:500000",
        # frame=['z20+l"Built-up-grid"', "wsNEZ", "af"],
        perspective=[180, 60],  # azimuth, elevation
        zscale=0.005,  # vertical exaggeration
        cmap=True,  # use colormap from makecpt
        style="o50u",  # 3-D column of size 50 units
    )

# Plot title text and some labels
fig.text(
    position="TL",
    offset="0.2c/-1.4c",
    text="Daerah Brunei-Muara",
    font="10p,NewCenturySchlbk-Italic,grey",
    angle=20,
    perspective=True,
    projection="z",
)
fig.text(
    x=294_000,
    y=550_000,
    text="Teluk Brunei",
    font="8p,grey",
    angle=30,
    perspective=True,
    projection="z",
)
fig.text(
    x=285_000,
    y=545_000,
    text="Jambatan SOAS",
    font="6p,grey",
    angle=-35,
    perspective=True,
    projection="z",
)

fig.savefig(fname="day23_human_settlement.png")
fig.show()
