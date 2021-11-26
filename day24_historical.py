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
# # Day 24 : Historical
#
# Historical data, historical style or something else.

# %%
import shutil
import zipfile

import pygmt
import geopandas as gpd
import requests

# %% [markdown]
# ## Download Middle Earth data!
#
# GIS layers for Middle Earth! Includes a 50m spatial resolution DEM in GeoTIFF
# format and various shapefiles of vector features. Retrieved from
# https://doi.org/10.21220/rkez-x707 or https://scholarworks.wm.edu/asoer/3
#
# Inspired by:
# - https://twitter.com/pokateo_/status/1458844709116391425
# - https://www.esri.com/arcgis-blog/products/story-maps/mapping/mapping-a-better-route-from-the-shire-to-mount-doom/

# %%
for file, url in [
    (
        "DEM_50m_Quad1.zip",
        "https://scholarworks.wm.edu/cgi/viewcontent.cgi?filename=4&article=1002&context=asoer&type=additional",
    ),
    (
        "Vector_Only_Shapefiles.zip",
        "https://scholarworks.wm.edu/cgi/viewcontent.cgi?filename=0&article=1002&context=asoer&type=additional",
    ),
]:
    response = requests.get(url=url, stream=True)
    with open(file=file, mode="wb") as out_file:
        shutil.copyfileobj(response.raw, out_file)

# %%
# Unzip the files
for file in ["DEM_50m_Quad1.zip", "Vector_Only_Shapefiles.zip"]:
    with zipfile.ZipFile(file=file) as z:
        for zip_info in z.infolist():
            z.extract(member=zip_info)

# %%
# Inspect the metadata of the GeoTIFF file
print(pygmt.grdinfo(grid="Quad1/DEM_50m_Quad1.tif"))

# %%
# Load vector shapefiles into GeoDataFrame
gdf_towns = gpd.read_file(filename="Vector_Shapefiles/Towns.shp")
gdf_roads = gpd.read_file(filename="Vector_Shapefiles/Roads.shp")

# %% [markdown]
# ## Clip data to The Shire
#
# Middle Earth is a big place, so we'll do a spatial subset to
# Hobbiton in The Shire to keep things simple. Using the x and y
# coordinates and geopandas' coordinate based indexer at
# https://geopandas.org/en/v0.10.2/docs/reference/api/geopandas.GeoDataFrame.cx.html
# to clip the town and road geodataframe layers

# %%
# gdf_shire_towns = gdf_towns.query(expr="Realm == 'The Shire'")
gdf_shire_towns = gdf_towns.cx[3_060_000:3_090_000, 2_722_000:2_740_000]
gdf_shire_towns


# %%
gdf_shire_roads = gdf_roads.cx[3_060_000:3_090_000, 2_722_000:2_740_000]
gdf_shire_roads

# %% [markdown]
# ## Plot the map!
#
# There are quite a few elements to this:
#
# 1. For the base layer, we'll use a parchment-like colour
#    as the background, and overlay a transparent-ish
#    copper-tone shaded DEM on top to get an aged-paper-like
#    effect
#
# 2. The road lines are plotted, with road name labels
#    placed to follow the road line using
#    `fig.plot(style="q...")`, see the `-Sq` option in
#    https://docs.generic-mapping-tools.org/6.2/plot.html#s
#    for more details.
#
# 3. Each town is plotted as a black square symbol, and
#    the corresponding label is plotted next to it, justified
#    manually so that it doesn't overlap with other elements
#
# 4. A title is placed on the top left corner of the map using an
#    old school cursive font. List of GMT Postscript fonts are at
#    https://docs.generic-mapping-tools.org/6.2/cookbook/postscript-fonts.html
#
# 5. Finally, we'll include an overly fancy directional compass
#    rose and map scale on two corners of the map.

# %%
fig = pygmt.Figure()

# Plot DEM
with pygmt.config(PS_PAGE_COLOR="#f7f3ea"):
    fig.grdimage(
        grid="Quad1/DEM_50m_Quad1.tif",
        cmap="copper",
        dpi=50,
        region=[3_060_000, 3_090_000, 2_722_000, 2_740_000],  # Hobbiton
        projection="x1:200000",
        shading=True,
        transparency=50,
    )

# Draw the road lines
fig.plot(data=gdf_shire_roads, pen="1p,gray10", style='qn1:+l""')
# Overlay road name one by one (using quoted line)
for _, road in gdf_shire_roads.iterrows():
    fig.plot(
        data=road.geometry,
        style=f'qn1:+l"{road.Name}"+f8p,Palatino-BoldItalic,gray10+i+jBC+v',
    )

# Plot towns as squares
fig.plot(
    x=gdf_shire_towns.geometry.x,
    y=gdf_shire_towns.geometry.y,
    style="s0.3c",
    color="black",
)
# Overlay town names one by one
for _, town in gdf_shire_towns.iterrows():
    justify = "TL" if town.Name == "Bywater" else "BR"
    text = town.Name.split()[0]
    fig.text(
        x=town.geometry.x,
        y=town.geometry.y,
        text=text,
        justify=justify,
        offset="j0.1c/0.2c",
        font="12p,NewCenturySchlbk-BoldItalic",
    )

# Plot title text on top left corner
fig.text(
    position="TL",
    text="The Shire",
    offset="0.7c/-0.7c",
    font="36p,ZapfChancery-MediumItalic,black",
)

# Plot directional rose on top right corner
# https://docs.generic-mapping-tools.org/6.2/cookbook/features.html#placing-dir-map-roses
with pygmt.config(FONT_TITLE="10p,ZapfChancery-MediumItalic"):
    fig.basemap(rose="jTR+w1.5c+f3+l+o1c")

# Plot a scalebar on bottom left corner, need to give
# a random projection and region for fancy scale to work
# https://docs.generic-mapping-tools.org/6.2/cookbook/features.html#placing-map-scales
with pygmt.config(FONT_LABEL="ZapfChancery-MediumItalic"):
    fig.basemap(
        region=[-130, -70, 24, 52],
        projection="EPSG:3034",
        map_scale="jBL+w500M+lMiles+f+o0.5c",
    )

fig.savefig(fname="day24_historical.png")
fig.show()
