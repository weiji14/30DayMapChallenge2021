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
# # Day 19 : Islands
#
# Islands in the water.

# %%
import geopandas as gpd
import pygmt
import rioxarray
import xarray as xr

# %% [markdown] tags=[]
# ## Download and preprocess Sentinel 2 true colour imagery
#
# Using relatively cloud-free imagery over Tuvalu on 12 Nov 2021.
# Data search was done using EO Browser. Link is at
# https://apps.sentinel-hub.com/eo-browser/?zoom=12&lat=-8.53434&lng=179.08779&themeId=DEFAULT-THEME&visualizationUrl=https://services.sentinel-hub.com/ogc/wms/bd86bcc0-f318-402b-a145-015f85b9427e&datasetId=S2L2A&fromTime=2021-11-12T00:00:00.000Z&toTime=2021-11-12T23:59:59.999Z&layerId=1_TRUE_COLOR
#
# The AWS URLs were discovered using intake-stac.
# I've omitted the code for brevity, but you can follow
# https://github.com/intake/intake-stac/blob/0.3.0/examples/aws-earth-search.ipynb
# to find out how the links to the Cloud Optimized GeoTiff files are obtained.

# %%
band4 = rioxarray.open_rasterio(
    filename="https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/60/L/YR/2021/11/S2A_60LYR_20211112_0_L2A/B04.tif",
    # masked=True,
    # overview_level=1,
)
band4["band"] = 4 * band4.band
band3 = rioxarray.open_rasterio(
    filename="https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/60/L/YR/2021/11/S2A_60LYR_20211112_0_L2A/B03.tif",
    # masked=True,
    # overview_level=1,
)
band3["band"] = 3 * band3.band
band2 = rioxarray.open_rasterio(
    filename="https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/60/L/YR/2021/11/S2A_60LYR_20211112_0_L2A/B02.tif",
    # masked=True,
    # overview_level=1,
)
band2["band"] = 2 * band2.band

# %%
# Stack the Red (4), Green (3) and Blue (2) bands together
band432 = xr.concat(objs=[band4, band3, band2], dim="band")

# %%
# Clip Sentinel 2 imagery to Funafuti, Tuvalu
band432_clipped = band432.rio.clip_box(
    minx=740900, maxx=743000, miny=9056000, maxy=9059050
)
# band432_clipped = band432.rio.clip_box(minx=720000, maxx=745000, miny=9042500, maxy=9075000)

# %%
# Normalize from 16-bit to 8-bit colors
b432 = (
    (band432_clipped - band432_clipped.min())
    / (band432_clipped.max() - band432_clipped.min())
) * 2 ** 8

# %%
# Save preprocessed Sentinel 2 image to a GeoTIFF file
b432.rio.to_raster(raster_path="B432_Tuvalu.tif", dtype="uint8")

# %%
# Inspect the GeoTIFF file's metadata
print(pygmt.grdinfo(grid="B432_Tuvalu.tif"))

# %% [raw]
# # If you want to download the actual GeoTIFF directly
# for band in ["B04", "B03", "B02"]:
#     pygmt.which(
#         fname=f"https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/60/L/YR/2021/11/S2A_60LYR_20211112_0_L2A/{band}.tif",
#         download=True,
#     )

# %% [markdown]
# ## Download Tuvalu Coastline data
#
# GeoJSON file sourced from
# https://tuvalu-data.sprep.org/dataset/tuvalu-coast-gis-data

# %%
_ = pygmt.which(
    fname="https://tuvalu-data.sprep.org/system/files/TUV_coast.geojson",
    download=True,
)

# %%
# Read GeoJSON file and reproject multipolygons
gdf = gpd.read_file(filename="TUV_coast.geojson")
gdf = gdf.to_crs(epsg=32760)  # reproject to EPSG:32760 (UTM Zone 60S)
print(gdf)

# %% [markdown]
# ## Plot the map!
#
# Let's make a map of Funafuti, Tuvalu. We'll plot the satellite imagery using PyGMT's
# [`grdimage`](https://www.pygmt.org/v0.5.0/api/generated/pygmt.Figure.grdimage.html).
# On the top right corner, we'll also plot an overview map of the entire atoll
# using [`inset`](https://www.pygmt.org/v0.5.0/api/generated/pygmt.Figure.inset.html).

# %%
fig = pygmt.Figure()

# Plot main map over main area of Funafuti where airport is located
region = [740900, 743000, 9056000, 9059050]
fig.grdimage(
    grid="B432_Tuvalu.tif",  # Sentinel2 image layer
    region=region,
    projection="x1:20000",
    frame=["lESt", "a1000f"],
)

# Plot overview map of entire Funafuti atoll
with fig.inset(position="jTR+w3c+o0.2c", box="+gturquoise4+p1p+r30p"):
    fig.plot(
        data=gdf,
        color="lightbrown",
        pen="1p,black",
        close=True,  # close polygons to colour them
        region=[720000, 745000, 9042500, 9070000],
        projection="X?",
    )
    rectangle = [[region[0], region[2], region[1], region[3]]]
    fig.plot(data=rectangle, style="r+s", pen="2p,blue")

# Plot title text
fig.text(
    position="BR",  # bottom right
    offset="-0.5c/0.5c",
    text="Funafuti, Tuvalu",
    font="24p,Bookman-LightItalic,turquoise3",
)

fig.savefig(fname="day19_islands.png")
fig.show()
