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
# # Day 27 : Heatmap
#
# A heat map (or heatmap) is a data visualization technique that
# shows magnitude of a phenomenon as color in two dimensions.
# The variation in color may be by hue or intensity, giving
# obvious visual cues to the reader about how the phenomenon is
# clustered or varies over space. (Source:
# [Wikipedia](https://en.wikipedia.org/wiki/Heat_map))

# %%
import numpy as np
import pandas as pd
import pygmt
import xarray as xr

# %% [markdown]
# ## Get Sea Surface Temperature Data
#
# Using the Sea Surface Temperature Daily Analysis:
# European Space Agency Climate Change Initiative product version 2.1
# which includes data spanning from late 1981 to recent time (31 Dec 2020).
# Data product available in Zarr format at
# https://registry.opendata.aws/surftemp-sst
#
# Specifically, we'll use this dataset to derive mean SST for the month
# of November over a standard 30 year time period from 1991 to 2020.
# To save on computation time, this will be run on a spatial subset over
# latitudes 60S-60N only.
#
# References:
# - Merchant, C. J., Embury, O., Bulgin, C. E., Block, T., Corlett, G. K., Fiedler, E., Good, S. A., Mittaz, J., Rayner, N. A., Berry, D., Eastwood, S., Taylor, M., Tsushima, Y., Waterfall, A., Wilson, R., & Donlon, C. (2019). Satellite-based time-series of sea-surface temperature since 1981 for climate applications. Scientific Data, 6(1), 223. https://doi.org/10.1038/s41597-019-0236-x
# - https://github.com/surftemp/sst-data-tutorials
# - https://niwa.co.nz/our-science/climate/information-and-resources/common-climate-weather-terms
# - https://gis.stackexchange.com/questions/205871/xarray-slicing-across-the-antimeridian/205900#205900

# %%
# Load Sea Surface Temperature (SST) time-series data
ds: xr.Dataset = xr.open_dataset(
    "s3://surftemp-sst/data/sst.zarr",
    engine="zarr",
    backend_kwargs=dict(storage_options={"anon": True}),
)

# %%
# Spatial subset to tropical and sub-tropical regions
ds_tropics = ds.sel(lat=slice(-60, 60))  # .isel(lon=(ds.lon < -80.0) | (ds.lon > 100))

# %%
# Temporal subset to 1991-2020, for the month of November only
ds_november = ds_tropics.sel(time=(ds_tropics.time.dt.month == 11))
ds_subset = ds_november.sel(time=slice("1991-01-01", "2020-12-31"))
ds_subset

# %%
# Get mean November SST over 1991-2020 time period
# Note, this calculation will take a while to runTemperature
da_mean_sst: xr.DataArray = ds_subset.analysed_sst.mean(dim="time", skipna=True)
da_mean_sst.to_netcdf("mean_nov_sst_1991-2020.nc")  # Save to NetCDF file

# %%
# Inspect the metadata of the GeoTIFF file
print(pygmt.grdinfo(grid="mean_nov_sst_1991-2020.nc"))

# %%
# Reload NetCDF from file (save on reprocessing again)
da_mean_sst: xr.DataArray = xr.open_dataarray(
    filename_or_obj="mean_nov_sst_1991-2020.nc"
)
da_mean_sst

# %% [markdown]
# ## Get SST anomaly between 24 Nov 2021 and 1991-2020 mean SST
#
# Obtaining the Sea Surface Temperature from Remote Sensing Systems, see
# https://www.remss.com/measurements/sea-surface-temperature/oisst-description.
# NetCDF donwloaded from
# https://data.remss.com/SST/daily/mw_ir/v05.0/netcdf/2021.
# We'll calculating the temperature difference between the observed sea surface
# temperatures from this grid and the 1991-2020 climate period.

# %%
# Download the NetCDF file
_ = pygmt.which(
    fname="https://data.remss.com/SST/daily/mw_ir/v05.0/netcdf/2021/20211124120000-REMSS-L4_GHRSST-SSTfnd-MW_IR_OI-GLOB-v02.0-fv05.0.nc",
    download=True,
)

# %%
# Load the NetCDF file
ds_sst_20211124: xr.Dataset = xr.open_dataset(
    filename_or_obj="20211124120000-REMSS-L4_GHRSST-SSTfnd-MW_IR_OI-GLOB-v02.0-fv05.0.nc",
)
ds_sst_20211124.analysed_sst.isel(time=0, drop=True)

# %%
# Interpolate mean SST grid to same coordinates as 20211124 SST grid
da_mean_sst_interp: xr.DataArray = da_mean_sst.interp_like(
    other=ds_sst_20211124, method="linear"
)

# %%
# Find difference (anomaly) of SST between 20211124 and 30 yr period
grid: xr.DataArray = ds_sst_20211124.analysed_sst.isel(time=0) - da_mean_sst_interp

# Manually set grid back to be Geographic/Pixel registered
grid.gmt.gtype = 1  # Geographic type
grid.gmt.registration = 1  # Pixel registration

# %% [markdown]
# ## Plot the 'heat' map!
#
# Now to plot the sea surface temperature anomaly grid!
# These are the step by step instructions
#
# 1. Use [`pygmt.makecpt`](https://www.pygmt.org/v0.5.0/api/generated/pygmt.makecpt.html)
#    to make a blue-red diverging colormap from -10°C to 10°C, with the white part
#    centred on zero.
#
# 2. Plot the anomaly grid using
#    [`fig.grdimage`](https://www.pygmt.org/v0.5.0/api/generated/pygmt.Figure.grdimage.html)
#    centred on the dateline with a
#    [`Mollweide`](https://www.pygmt.org/v0.5.0/projections/misc/misc_mollweide.html)
#    projection which is a pseudo-cylindrical, equal-area projection.
#    You can play around with different map projections at
#    https://kartograph.org/showcase/projections/#mollweide
#
# 3. Finally, plot a color scale using
#    [`fig.colorbar`](https://www.pygmt.org/v0.5.0/api/generated/pygmt.Figure.colorbar.html)
#    on the bottom so people know what the colors refer to.

# %%
fig = pygmt.Figure()

pygmt.makecpt(cmap="vik+h0", series=(-10, 10, 2), continuous=True)
fig.grdimage(
    grid=grid,
    region=[-180, 180, -60, 60],
    projection="W180/21c",
    cmap=True,
    # Title is set with +t, subtitle is set with +s
    frame=[
        'wSnE+t"Sea Surface Temperature Anomaly"+s"24 Nov 2021 minus 1991-2020 Nov mean"',
        "af",
    ],
)
fig.colorbar(
    position="JMR+o1c/0c+w6c/0.3c+n+e", frame=['x+l"Colder <-> Warmer"', r"y+l\260C"]
)

fig.savefig(fname="day27_heatmap.png")
fig.show()
