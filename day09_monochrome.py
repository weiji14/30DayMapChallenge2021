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
# # Day 9 : Monochrome
#
# A monochromic image is composed of one color (or values of one color).

# %%
import pygmt

# %% [markdown]
# Download the Landsat 9 First Light image
# over Kimberley Coast in Western Australia
# from https://svs.gsfc.nasa.gov/13987.

# %%
tif_file = pygmt.which(
    fname="https://svs.gsfc.nasa.gov/vis/a010000/a013900/a013987/L9_Australia_20211031_p109r070-lrg.tif",
    download=True,
)

# %%
# Inspect the raw TIF file's metadata
print(pygmt.grdinfo(grid=tif_file))

# %% [markdown]
# Perform histogram equalization to stretch the 16-bit color image
# (note that Landsat 9's OLI sensor has a 14-bit radiometric resolution)
# into 8-bit. I.e. 65536 to 256. We'll be using
# [`grdhisteq`](https://docs.generic-mapping-tools.org/6.2/grdhisteq.html)
# for this, you can learn more about how it works at
# https://docs.generic-mapping-tools.org/6.2/gallery/ex38.html.

# %%
!gmt grdhisteq -C256 {tif_file} -GL9_Australia_20211031_p109r070-lrg-histeq.tif

# %%
# Inspect the histogram equalized TIF file's metadata
print(pygmt.grdinfo(grid="L9_Australia_20211031_p109r070-lrg-histeq.tif"))

# %% [markdown]
# Now to plot the Landsat 9 image! We'll use PyGMT's
# [`makecpt`](https://www.pygmt.org/v0.5.0/api/generated/pygmt.makecpt.html) and
# [`grdimage`](https://www.pygmt.org/v0.5.0/api/generated/pygmt.Figure.grdimage.html)
# functions to do so and plot it in grayscale!

# %%
fig = pygmt.Figure()
pygmt.makecpt(cmap="grayC", series=[0, 256, 1], reverse=True)
fig.grdimage(
    grid="L9_Australia_20211031_p109r070-lrg-histeq.tif",
    cmap=True,
    nan_transparent=True,
)
fig.savefig(fname="day09_monochrome.png")
fig.show()

# %% [markdown]
# P.S. If you're interested in more colormaps, see
# https://docs.generic-mapping-tools.org/6.2/cookbook/cpts.html#id3.
# I highly recommend chosing a [Scientific Colour Map](http://www.fabiocrameri.ch/colourmaps.php) too!
