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
# # Day 12 : Population
#
# Counting cute megafauna!

# %%
import os
import zipfile

import pandas as pd
import pygmt
import pyproj
import rioxarray

# %% [markdown]
# ## Download Adélie Penguin population counts
#
# Getting the number of Adélie penguin (*Pygoscelis adeliae*; ADPE) scattered across
# colonies in Antarctica. Open data sourced from
# https://github.com/pointblue/ContinentalWESEestimates/tree/v1.0/data.
#
# References:
# - Lynch, H. J., & LaRue, M. A. (2014). First global census of the Adélie Penguin. The Auk, 131(4), 457–466. https://doi.org/10.1642/AUK-14-31.1
# - LaRue, M. A., Salas, L., Nur, N., Ainley, D., Stammerjohn, S., Pennycook, J., Dozier, M., Saints, J., Stamatiou, K., Barrington, L., & Rotella, J. (2021). Insights from the first global population estimate of Weddell seals in Antarctica. Science Advances, 7(39), eabh3674. https://doi.org/10.1126/sciadv.abh3674

# %%
df = pd.read_csv(
    filepath_or_buffer="https://github.com/pointblue/ContinentalWESEestimates/raw/v1.0/data/ADPE_colonies_20200416.csv"
)

# %%
# Reproject from EPSG:4326 to EPSG:3031
proj = pyproj.Transformer.from_crs(crs_from=4326, crs_to=3031, always_xy=True)
df["x"], df["y"] = proj.transform(xx=df.Longitude, yy=df.Latitude)

# %%
# Subset to locations inside region of interest
df = pygmt.select(
    data=df[["x", "y", "ADPEcount", "ADPEname"]],
    region=[150_000, 600_000, -2_100_000, -1_180_000],
)
df = df.sort_values(by="ADPEcount")
df

# %% [markdown] tags=[]
# ## Download Landsat Image Mosaic Of Antarctica (LIMA)
#
# Cloud-free mosaic of Antarctica derived from Landsat imagery.
# Offical site is at https://lima.usgs.gov,
# download product from https://lima.usgs.gov/fullcontinent.php

# %%
# Download and unzip LIMA GeoTIFF file
pygmt.which(fname="https://lima.usgs.gov/tiff_90pct.zip", download=True)
with zipfile.ZipFile(file="tiff_90pct.zip") as z:
    for zip_info in z.infolist():
        if zip_info.filename.endswith(".tif"):
            zip_info.filename = os.path.basename(zip_info.filename)
            z.extract(member=zip_info)

# %%
# Crop to our region of interest in the Eastern part of the Ross Sea
with rioxarray.open_rasterio(filename="00000-20080319-092059124.tif") as rds:
    rds_cropped = rds.rio.clip_box(
        minx=150_000, maxx=600_000, miny=-2_100_000, maxy=-1_180_000
    )
    rds_cropped.rio.to_raster("LIMA_cropped.tif")

# %%
# Inspect the GeoTIFF file's metadata
print(pygmt.grdinfo(grid="LIMA_cropped.tif"))

# %% [markdown]
# ## Plot the map!
#
# Time to map this up! We'll use PyGMT's
# [`grdimage`](https://www.pygmt.org/v0.5.0/api/generated/pygmt.Figure.grdimage.html)
# to lay down the background LIMA imagery, and plot the Penguin colony location
# points colour coded by the population count. Those with a count of more than 50000
# will have their place name labelled, and we'll include a colorbar and title too!

# %%
fig = pygmt.Figure()
# Background LIMA colour image
fig.grdimage(
    grid="LIMA_cropped.tif",
    img_in="r",
    region=[150_000, 600_000, -2_100_000, -1_180_000],
    projection="x1:5000000",
    frame=["lESt", "xaf", "ya200000f"],
)
# Plot penguin colony counts from dataframe
pygmt.makecpt(cmap="bilbao", series=[0, 300_000, 50_000])
fig.plot(
    x=df.x,
    y=df.y,
    color=df.ADPEcount,
    cmap=True,
    pen="thin,snow",
    style="d0.2c",
)
# Place names of colonies with > 50000 penguins are labelled
# Plot black text on a dark gray background halo
df_top = df.query(expr="ADPEcount > 50000")
for font_style in ["AvantGarde-DemiOblique,darkgray", "AvantGarde-BookOblique,black"]:
    fig.text(
        x=df_top.x,
        y=df_top.y,
        text=df_top.ADPEname,
        font=f"7p,{font_style}",
        justify="BC",
        offset="j0.2c",
    )
# Add a colorbar and title to the plot for context
with pygmt.config(FONT_ANNOT="7p,white", MAP_FRAME_PEN="0.5p,white"):
    fig.colorbar(position="JBL+jBL+ef+o0.2c/1.2c+w3c/0.2c")
fig.text(
    position="BL",
    offset="0.2c/0.6c",
    text="Adélie Penguin population",
    font="10p,AvantGarde-DemiOblique,white",
)
fig.text(
    position="BL",
    offset="1.8c/0.2c",
    text="Eastern Ross Sea",
    font="10p,AvantGarde-DemiOblique,white",
)
fig.savefig(fname="day12_population.png")
fig.show()
