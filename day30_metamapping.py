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
# # Day 30 : Metamapping day
#
# Final day! Spend the day either by:
# 1. collecting your entries from the challenge to a common gallery,
# 2. writing a tutorial or a blog post on one of your maps or
# 3. create a map from a theme you have chosen yourself

# %%
import os
import zipfile

import fiona
import geopandas as gpd
import pygmt

# %% [markdown]
# ## Download image files
#
# All of these are available at
# https://github.com/weiji14/30DayMapChallenge2021/releases

# %%
# Download image files
files = [
    "https://github.com/weiji14/30DayMapChallenge2021/releases/download/v0.1.0/day08_blue.png",
    "https://github.com/weiji14/30DayMapChallenge2021/releases/download/v0.1.0/day09_monochrome.png",
    "https://github.com/weiji14/30DayMapChallenge2021/releases/download/v0.1.0/day10_raster.png",
    "https://github.com/weiji14/30DayMapChallenge2021/releases/download/v0.1.0/day11_3d.png",
    "https://github.com/weiji14/30DayMapChallenge2021/releases/download/v0.1.0/day12_population.png",
    "https://github.com/weiji14/30DayMapChallenge2021/releases/download/v0.1.0/day13_natural_earth.png",
    "https://github.com/weiji14/30DayMapChallenge2021/releases/download/v0.1.0/day14_new_tool_opttransp.gif",
    "https://github.com/weiji14/30DayMapChallenge2021/releases/download/v0.2.0/day15_without_computer.jpg",
    "https://github.com/weiji14/30DayMapChallenge2021/releases/download/v0.2.0/day16_urban.png",
    "https://github.com/weiji14/30DayMapChallenge2021/releases/download/v0.2.0/day17_land.png",
    "https://github.com/weiji14/30DayMapChallenge2021/releases/download/v0.2.0/day18_water.png",
    "https://github.com/weiji14/30DayMapChallenge2021/releases/download/v0.2.0/day19_islands.png",
    "https://github.com/weiji14/30DayMapChallenge2021/releases/download/v0.2.0/day20_movement.gif",
    "https://github.com/weiji14/30DayMapChallenge2021/releases/download/v0.2.0/day21_elevation.png",
    "https://github.com/weiji14/30DayMapChallenge2021/releases/download/v0.3.0/day22_boundaries.png",
    "https://github.com/weiji14/30DayMapChallenge2021/releases/download/v0.3.0/day23_human_settlement.png",
    "https://github.com/weiji14/30DayMapChallenge2021/releases/download/v0.3.0/day24_historical.png",
    "https://github.com/weiji14/30DayMapChallenge2021/releases/download/v0.3.0/day25_interactive.gif",
    "https://github.com/weiji14/30DayMapChallenge2021/releases/download/v0.3.0/day26_choropleth.png",
    "https://github.com/weiji14/30DayMapChallenge2021/releases/download/v0.3.0/day27_heatmap.png",
    "https://github.com/weiji14/30DayMapChallenge2021/releases/download/v0.3.0/day28_round_earth.png",
    "https://github.com/weiji14/30DayMapChallenge2021/releases/download/v0.3.0/day29_null.png",
]
pygmt.which(fname=files, download=True)

# %% [markdown]
# ## Make a gallery!
#
# We'll make a gallery using
# [`fig.subplot`](https://www.pygmt.org/v0.4.1/api/generated/pygmt.Figure.subplot.html) and
# [`fig.image`](https://www.pygmt.org/v0.5.0/api/generated/pygmt.Figure.image.html)!

# %%
fig = pygmt.Figure()

with fig.subplot(nrows=4, ncols=6, figsize=("22c", "14c"), frame="+n"):
    # First panel will have text
    fig.text(
        position="CM",
        text="30DayMapChallenge",
        region="d",
        angle=45,
        no_clip=True,
        panel=0,
    )
    fig.text(
        position="CM", text="2021", region="d", angle=45, offset="0.5c/-0.3c", panel=0
    )

    # Middle panels will have individual images
    for i, file in enumerate(files, start=1):
        imagefile = os.path.basename(file)
        fig.image(imagefile=imagefile, region="d", position=f"jMC+w3c", panel=i)

    # Last panel will have more text
    fig.text(
        position="CM",
        text="Maps made with",
        region="d",
        angle=45,
        no_clip=True,
        panel=23,
    )
    fig.text(
        position="CM",
        text="PyGMT*",
        region="d",
        angle=45,
        offset="0.7c/-0.3c",
        panel=23,
    )

fig.savefig(fname="day30_metamapping.png")
fig.show()
