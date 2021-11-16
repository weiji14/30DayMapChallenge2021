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
# # Day 16 : Urban/Rural
#
# Map an urban area or rural area. Or something that defines that place.

# %%
import zipfile

import pygmt

# %% [markdown]
# ## Download Wellington City Urban Aerial Photos
#
# Getting some Orthophotography of urban areas within Wellington City taken in
# the flying season (austral summer period). We'll compare imagery taken 8 years
# apart - an older 10cm spatial resolution image from 2012/2013 and a newer
# 7.5cm spatial resolution image from 2020/2021.
#
# Links to the data at LINZ Data Service (LDS):
# - https://data.linz.govt.nz/layer/105744-wellington-city-0075m-urban-aerial-photos-2021
# - https://data.linz.govt.nz/layer/51871-wellington-01m-urban-aerial-photos-2012-2013
#
# Specfically, we'll get a specific tile which covers a section of
# [Cuba Street](https://www.wellingtonnz.com/visit/cuba-street) in Te Aro,
# one of the coolest parts of Wellington!
# - [BQ31_500_041070](https://data.linz.govt.nz/layer/105744-wellington-city-0075m-urban-aerial-photos-2021/data/504/?mt=Streets&l=105749%2C105744%3A0&lpw=650&cv=0&z=17&c=-41.29187%2C174.77743&e=0&al=m&lag_f=*&lag_q=BQ31_500_041070) from 2020/2021
# - [BQ31_041070](https://data.linz.govt.nz/layer/51871-wellington-01m-urban-aerial-photos-2012-2013/data/72/?mt=Streets&l=51871&lpw=650&cv=0&z=15&c=-41.29422%2C174.77575&e=0&al=m&lag_f=*&lag_q=BQ31_041070) from 2012/2013
#
# You'll need to manually create a LINZ Data Service account, login, and
# download a zipped GeoTIFF. Choose the default EPSG:2193 projection,
# 'TIFF' as the image option, and 'Original Resolution'.
#
# ![Download settings on LDS](https://user-images.githubusercontent.com/23487320/141964407-f2a06171-7767-423f-8e07-a32c8ed21865.png)

# %%
# Unzip the files
for file in ["lds-tile-bq31-500-041070-GTiff.zip", "lds-tile-bq31-041070-GTiff.zip"]:
    with zipfile.ZipFile(file=file) as z:
        for zip_info in z.infolist():
            z.extract(member=zip_info)

# %%
# Inspect the metadata of the GeoTIFF files
print(pygmt.grdinfo(grid="BQ31_500_041070.tif"))
print(pygmt.grdinfo(grid="BQ31_041070.tif"))

# %% [markdown]
# ## Plot the map!
#
# Let's plot the two images side by side using
# [pygmt.Figure.subplot](https://www.pygmt.org/v0.5.0/api/generated/pygmt.Figure.subplot.html)
# and [pygmt.Figure.set_panel](https://www.pygmt.org/v0.5.0/api/generated/pygmt.Figure.set_panel.html)
# (see tutorial at https://www.pygmt.org/v0.5.0/tutorials/subplots.html).
# The RGB GeoTIFFs are plotted using the
# [`grdimage`](https://www.pygmt.org/v0.5.0/api/generated/pygmt.Figure.grdimage.html)
# function.

# %%
import pygmt

# %%
fig = pygmt.Figure()

with pygmt.config(FONT_TAG="AvantGarde-Demi,225/221/0"):
    with fig.subplot(
        ncols=2,
        subsize=("8c", "12c"),
        autolabel=True,
        sharex="b",
        sharey="r",
        frame=["lEtS", "xa100f", "yaf"],
    ):
        # Plot 2012/2013 image on the left
        with fig.set_panel(panel=0, fixedlabel="2012/2013"):
            fig.grdimage(grid="BQ31_041070.tif")

        # Plot 2020/2021 image on the right
        with fig.set_panel(panel=1, fixedlabel="2020/2021"):
            fig.grdimage(grid="BQ31_500_041070.tif")

# fig.savefig(fname="day16_urban.png")
fig.show()
