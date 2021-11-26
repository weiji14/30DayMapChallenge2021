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
# # Day 25 : Interactive map
#
# What if the user wants to click, pan and explore your map?

# %%
import panel as pn
import param
import pygmt
import xarray as xr

pn.extension()

# %% [markdown]
# ## Make panel widgets
#
# [Panel](https://panel.holoviz.org/index.html) is a Python library
# for connecting interactive widgets with plots! We'll use Panel with
# [PyGMT](https://www.pygmt.org) to explore different colour maps and
# projections for the Earth
#
# - Scientific Colour Maps in GMT: https://docs.generic-mapping-tools.org/6.2/cookbook/cpts.html#id2
# - Projections: https://www.pygmt.org/v0.5.0/projections

# %%
cmap = pn.widgets.RadioButtonGroup(
    name="Scientific Colour Maps",
    options=["batlow", "bukavu", "fes", "oleron"],
    button_type="success",
    sizing_mode="scale_width",
)
projection = pn.widgets.RadioButtonGroup(
    name="Projection Type",
    options={
        "Hammer": "H",
        "Sinusoidal": "I",
        "Miller Cylindrical": "J",
        "Robinson": "N",
        "Winkel Tripel": "R",
        "Mollweide": "W",
    },
)

# %% [markdown]
# ## Load earth_relief data and create plot function
#
# Getting SRTM15+V2.1 [earth_relief](https://docs.generic-mapping-tools.org/6.2/datasets/remote-data.html#global-earth-relief-grids)
# via [`pygmt.datasets.load_earth_relief`](https://www.pygmt.org/v0.5.0/api/generated/pygmt.datasets.load_earth_relief.html),
# and making a simple PyGMT `grdimage` function that takes a cmap
# and projection string as input.

# %%
grid: xr.DataArray = pygmt.datasets.load_earth_relief(resolution="01d")


# %%
@pn.depends(cmap.param.value, projection)
def view(cmap: str, projection: str):
    fig = pygmt.Figure()
    fig.grdimage(grid=grid, cmap=cmap, projection=f"{projection}180/20c")
    return fig


# %% [markdown]
# ## Make the interactive dashboard!
#
# Now to put everything together! The 'dashboard' will be very simple.
# The 'cmap' and 'projection' radio button chooser buttons is placed
# one after another vertically using `panel.Column`, and the map is
# then draw below. Toggling different buttons will update the map
# to use a new colormap or projection! For more info, go check out
# https://panel.holoviz.org/getting_started/index.html#using-panel
#
# Note: This is meant to run in a Jupyter lab/notebook environment.

# %%
pn.Column(cmap, projection, view)
