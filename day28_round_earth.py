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
# # Day 28 : The Earth is not flat
#
# The Earth isn’t flat (AFAIK), so how would you show that on a map?
# Maybe something creative with projections?

# %%
import pygmt

# %% [markdown]
# ## Plot the map!
#
# Let's keep things simple and plot an
# [Azimuthal Equidistant](https://www.pygmt.org/v0.5.0/projections/azim/azim_equidistant.html)
# projection map. More details about the projection are at
# https://docs.generic-mapping-tools.org/latest/cookbook/map-projections.html#azimuthal-equidistant-projection-je-je.
#
# The background will be NASA's Blue Marble imagery at 6 arc-minute resolution
# provided through the GMT data server, see
# https://docs.generic-mapping-tools.org/6.2/datasets/remote-data.html#global-earth-day-night-images
# for more details. The image will be shaded with some earth relief, and some
# gridlines will also be added on top. All of this will be done in a single
# [`fig.grdview`](https://www.pygmt.org/v0.5.0/api/generated/pygmt.Figure.grdview.html)
# function call!

# %%
fig = pygmt.Figure()

with pygmt.config(PS_PAGE_COLOR="black"):
    fig.grdview(
        grid="@earth_relief_06m_g",  # SRTM15+V2.1
        drapegrid="@earth_day_06m",  # Blue Marble
        surftype="i",
        shading="+a-45+nt0.25+m0",
        # Azimuthal Equidistant projection
        projection="E170/-30/179/12c",  # Elon0/lat0[/horizon]width
        region="d",
        frame=["xg60", "yg30"],
        perspective=180,  # rotate map by 180 (so South is up)
    )

fig.savefig(fname="day28_round_earth.png")
fig.show()
