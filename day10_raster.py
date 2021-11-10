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
# # Day 10 : Raster
#
# This day is dedicated to those lovely pixels!

# %%
import pygmt
import requests
import shutil

# %% [markdown]
# Download MODIS Terra true colour imagery
# over Glasgow, United Kingdom on 9 Nov 2021
# using Worldview Snapshots. Link is at
# https://wvs.earthdata.nasa.gov/?LAYERS=MODIS_Terra_CorrectedReflectance_TrueColor&CRS=EPSG:4326&TIME=2021-11-09&COORDINATES=55.0,-5.5,56.45,-3.55&FORMAT=image/tiff&AUTOSCALE=TRUE&RESOLUTION=250m

# %%
url = "https://wvs.earthdata.nasa.gov/api/v1/snapshot?REQUEST=GetSnapshot&LAYERS=MODIS_Terra_CorrectedReflectance_TrueColor&CRS=EPSG:4326&TIME=2021-11-09&WRAP=DAY&BBOX=55,-5.5,56.45,-3.55&FORMAT=image/tiff&WIDTH=887&HEIGHT=660&AUTOSCALE=TRUE&ts=1636541620482"
response = requests.get(url=url, stream=True)
with open("modis_img.tif", "wb") as out_file:
    shutil.copyfileobj(response.raw, out_file)

# %%
# Inspect the GeoTIFF file's metadata
print(pygmt.grdinfo(grid="modis_img.tif"))

# %% [markdown]
# Now to plot the MODIS true colour image! We'll use PyGMT's
# [`grdimage`](https://www.pygmt.org/v0.5.0/api/generated/pygmt.Figure.grdimage.html)
# function to do so and plot it in using the [EPSG:27700](https://epsg.io/27700)
# projection system!

# %%
fig = pygmt.Figure()
with pygmt.config(MAP_ANNOT_OBLIQUE="lat_parallel"):
    fig.grdimage(grid="modis_img.tif", projection="EPSG:27700", frame="af")
fig.savefig(fname="day10_raster.png")
fig.show()
