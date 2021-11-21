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
# # Day 21 : Elevation
#
# Sweet hillshades, beautiful contours, high mountains or low valleys.
# DEM, DSM or something else.

# %%
import pandas as pd
import pygmt
import requests
import rioxarray
import xarray as xr

# %% [markdown]
# ## Download ICESat-2 ATL08 data from OpenAltimetry
#
# [ICESat-2](https://en.wikipedia.org/wiki/ICESat-2) is a laser altimeter
# that shoots six laser beams down to Earth, basically a LiDAR in space!
# Here, we're getting the ATLAS/ICESat-2 L3A Land and Vegetation Height
# data product which covers the non-polar land regions. You can find the
# interactive viewer at https://openaltimetry.org/data/icesat2, and the
# API access point at https://openaltimetry.org/data/swagger-ui
#
# We'll be obtaining data over Taranaki Maunga/Mount Taranaki in Aotearoa.
# To see the photon data corresponding to this area, go to
# https://openaltimetry.org/data/icesat2/elevation?minx=174.00794688833005&miny=-39.36309060632322&maxx=174.16587535512693&maxy=-39.25391397058103&zoom_level=12&beams=1,2,3,4,5,6&tracks=595&date=2021-05-02&product=ATL08&mapType=geographic

# %%
# Build OpenAltimetry query parameters
minx, miny, maxx, maxy = [173.95, -39.39, 174.5, -39.20]
date: str = "2021-05-02"  # UTC date
track: int = 595  # reference ground track
# beam: int = 1  # 1 to 6
params: dict = {
    "client": "jupyter",
    "minx": minx,
    "miny": miny,
    "maxx": maxx,
    "maxy": maxy,
    "date": date,
    "trackId": str(track),
    # "beam": str(beam),
    "outputFormat": "json",
}

# %%
# Make OpenAltimetry data request, returning a JSON
r = requests.get(url="https://openaltimetry.org/data/api/icesat2/atl08", params=params)
print(len(r.json()["series"][0]["lat_lon_elev_canopy"]))

# %%
# Put JSON longitude/latitude/elevation/canopy data into a pandas DataFrame
df: pd.DataFrame = pd.json_normalize(
    data=r.json()["series"], record_path="lat_lon_elev_canopy"
)
df.rename(
    columns={0: "latitude", 1: "longitude", 2: "elevation", 3: "canopy"}, inplace=True
)
print(df)

# %% [raw]
# # Instead of using OpenAltimetry, a better way to get ICESat-2 data is via icepyx
# # This is an example of how you would get the ATL08 granules
# import icepyx as ipx
#
# region_mt_taranaki = ipx.Query(
#     dataset="ATL08",
#     spatial_extent=[173.7774915, -39.3252822, 173.8947362, -39.2671748],
#     version="4",
# )
# region_mt_taranaki.avail_granules(ids=True)

# %% [markdown]
# ## Download DEM of Taranaki Maunga
#
# Here, we'll use [`pygmt.grdcut`](https://www.pygmt.org/v0.5.0/api/generated/pygmt.grdcut.html)
# to get a 1 arc second spatial resolution Digital Elevation Model of Mount Taranaki.
# The grid will be cut into a circle with a 9.6 kilometres radius centred on the summit,
# corresponding to [Egmont National Park](https://en.wikipedia.org/wiki/Egmont_National_Park).

# %%
# Get a 1 arc second DEM of radius 9.6km around Mt Taranaki summit
grid = pygmt.grdcut(
    grid="@earth_relief_01s", circ_subregion="174:03:53E/39:17:47S/9.6k+n"
)
print(grid)

# %%
# Get longitude/latitude min/max bounds rounded to 0.01 and 0.1 degrees
region: str = pygmt.grdinfo(grid=grid, spacing=[0.01, 0.1])[2:].strip()
# Get elevation min/max bounds
region += "/" + pygmt.grdinfo(grid=grid, nearest_multiple=True)[2:].strip()
print(region)  # 173/175/-39.4/-39.2/-39.2379/2496

# %% [markdown]
# ## Download and preprocess Landsat 8 true colour imagery
#
# Using relatively cloud-free imagery over Taranaki on 26 May 2021.
# Data search was done using EO Browser. Link is at
# https://apps.sentinel-hub.com/eo-browser/?zoom=12&lat=-39.31232&lng=174.01846&themeId=DEFAULT-THEME&visualizationUrl=https%3A%2F%2Fservices.sentinel-hub.com%2Fogc%2Fwms%2Ffa073661-b70d-4b16-a6a9-e866825f05fd&datasetId=AWS_LOTL2&fromTime=2021-05-26T00%3A00%3A00.000Z&toTime=2021-05-26T23%3A59%3A59.999Z&layerId=1_TRUE_COLOR
#
# The AWS URLs were discovered using https://landsat-pds.s3.amazonaws.com/index.html
# You can also follow https://github.com/intake/intake-stac/blob/0.3.0/examples/aws-earth-search.ipynb
# to find out how the links to the Cloud Optimized GeoTiff files are obtained.

# %%
band4 = rioxarray.open_rasterio(
    filename="https://landsat-pds.s3.amazonaws.com/c1/L8/074/087/LC08_L1TP_074087_20210526_20210529_01_T1/LC08_L1TP_074087_20210526_20210529_01_T1_B4.TIF",
    # masked=True,
    # overview_level=1,
)
band4["band"] = 4 * band4.band
band3 = rioxarray.open_rasterio(
    filename="https://landsat-pds.s3.amazonaws.com/c1/L8/074/087/LC08_L1TP_074087_20210526_20210529_01_T1/LC08_L1TP_074087_20210526_20210529_01_T1_B3.TIF",
    # masked=True,
    # overview_level=1,
)
band3["band"] = 3 * band3.band
band2 = rioxarray.open_rasterio(
    filename="https://landsat-pds.s3.amazonaws.com/c1/L8/074/087/LC08_L1TP_074087_20210526_20210529_01_T1/LC08_L1TP_074087_20210526_20210529_01_T1_B2.TIF",
    # masked=True,
    # overview_level=1,
)
band2["band"] = 2 * band2.band

# %%
# Stack the Red (4), Green (3) and Blue (2) bands together
band432 = xr.concat(objs=[band4, band3, band2], dim="band")

# %%
# Reproject image from EPSG:32758 to EPSG:4326
band432_reprojected = band432.rio.reproject(dst_crs="EPSG:4326")

# %%
# Clip Sentinel 2 imagery to geographical extent of the DEM
b432 = band432_reprojected.rio.clip_box(
    minx=173.95, maxx=174.18, miny=-39.4, maxy=-39.2
)

# %%
# Normalize from 16-bit to 8-bit colors
b432_mt_taranaki = ((b432 - b432.min()) / (b432.max() - b432.min())) * 2 ** 8

# %%
# Save preprocessed Landsat 8 image to a GeoTIFF file
b432_mt_taranaki.rio.to_raster(raster_path="B432_Mt_Taranaki.tif", dtype="uint8")

# %%
# Inspect the GeoTIFF file's metadata
print(pygmt.grdinfo(grid="B432_Mt_Taranaki.tif"))

# %% [markdown]
# ## Plot the map!
#
# Let's use PyGMT's [`grdview`](https://www.pygmt.org/v0.5.0/api/generated/pygmt.Figure.grdview.html)
# to plot a 3D perspective surface coloured by the Landsat 8 true colour imagery.
# Some shading is applied to the 3D terrain to make it stand out more. Then,
# the ATL08 point cloud data will be plotted on top of this DEM surface using
# [`plot3d`](https://www.pygmt.org/v0.5.0/api/generated/pygmt.Figure.plot3d.html).

# %%
fig = pygmt.Figure()

# Plot the DEM draped by Landsat 8 imagery
with pygmt.config(PS_PAGE_COLOR="black"):
    fig.grdview(
        grid=grid,
        drapegrid="B432_Mt_Taranaki.tif",
        region=region,
        shading="+a33+nt0.6+m0.2",
        surftype="i600",  # image draping with 600dpi resolution
        perspective=[157.5, 20],
        zscale=0.002,
    )

# Plot the ATL08 point cloud
# pygmt.makecpt(cmap="bamako", series=(0, 3000, 100), reverse=True)
fig.plot3d(
    x=df.longitude,
    y=df.latitude,
    z=df.elevation,
    region=region,
    style="u0.03c",
    pen="thinnest,forestgreen",
    # color="+z",
    # cmap=True,
    # zvalue=True,
    perspective=True,
    zscale=True,
)

# Plot a title in the corner
fig.text(
    position="MC",  # middle centre
    offset="-3.3c/0c",
    text="Mt Taranaki",
    font="18p,ZapfChancery-MediumItalic,white",
)
fig.savefig(fname="day21_elevation.png", dpi=600)
fig.show()
