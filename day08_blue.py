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
# # Day 8 : Blue
#
# A map with blue colour or a map about something blue.

# %%
import pygmt

# %% [markdown]
# Create the day-night transition grid image

# %%
res = "03m"  # 3 arc minute resolution

# Use the location of the Sun at 8.00pm (sunset) on 8 Nov 2021, New Zealand Daylight Time (UTC+13)
!gmt solar -C -o0:1 -I+d2021-11-08T20:00+z13  # 70.935426882 -16.8076664681
# # Make a global grid with a smooth 2-degree transition across day/night boundary.
!gmt grdmath -Rd -I$res -r 70.935426882 -16.8076664681 2 DAYNIGHT = w.grd

# %% [markdown]
# Using GMT Remote datasets:
#
# - SRTM15+V2.1 [earth_relief](https://docs.generic-mapping-tools.org/6.2/datasets/remote-data.html#global-earth-relief-grids)
# - NASA Black Marble [earth_night](https://docs.generic-mapping-tools.org/6.2/datasets/remote-data.html#global-earth-day-night-images)

# %%
# We will create an intensity grid based on a DEM so that we can see structures in the oceans
pygmt.grdgradient(
    grid=f"@earth_relief_{res}", normalize="t0.5", azimuth=45, outgrid="intens.grd"
)

# Blend the earth_day and earth_night geotiffs using the weights, so that when w is 1
# we get the earth_day, and then adjust colors based on the intensity.
!gmt grdmix @earth_day_$res @earth_night_$res -Ww.grd -Iintens.grd -Gview.tif

# %% [markdown]
# Using the General Perspective projection, refer to
# https://www.pygmt.org/v0.5.0/projections/azim/azim_general_perspective.htmlhttps://docs.generic-mapping-tools.org/6.2/datasets/remote-data.html#global-earth-day-night-images

# %%
fig = pygmt.Figure()
# Plot this image of Earth with view over Wellington, New Zealand
with pygmt.config(PS_PAGE_COLOR="10/10/49"):  # dark blue background
    fig.grdimage(
        grid="view.tif",
        # General Perspective lon0/lat0/altitude/azimuth/tilt/twist/Width/Height/width
        projection="G-174.77299/-41.28667/1200/270/45/0/60/45/12c",
    )
fig.savefig(fname="day08_blue.png")
fig.show()
