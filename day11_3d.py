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
# # Day 11 : 3D
#
# The magnificent third dimension! Visualize something in 3D!

# %%
import pygmt
import rioxarray
import xarray as xr

# %% [markdown]
# ## Download Digital Elevation Model (DEM) over Scott Base, Antarctica
#
# Get the 1m Digital Elevation Model (DEM) from OpenTopography!
# This DEM was derived from 2014-2015 lidar survey of the McMurdo Dry Valleys, Antarctica.
# Data source is at https://portal.opentopography.org/raster?opentopoID=OTSDEM.112016.3294.1
#
# Reference:
# - Fountain, A. G., Fernandez-Diaz, J. C., Obryk, M., Levy, J., Gooseff, M., Van Horn, D. J., Morin, P., and Shrestha, R.: High-resolution elevation mapping of the McMurdo Dry Valleys, Antarctica, and surrounding regions, Earth Syst. Sci. Data, 9, 435-443, https://doi.org/10.5194/essd-9-435-2017, 2017

# %%
dem_file: str = pygmt.which(
    fname="https://opentopography.s3.sdsc.edu/raster/MDV_2014/MDV_2014_be/Capes_MCMD_Pegasus/Mcmd.tif",
    download=True,
)

# %%
# Inspect the GeoTIFF file's metadata
print(pygmt.grdinfo(grid=dem_file))

# %%
with rioxarray.open_rasterio(filename="Mcmd.tif") as dem_ds:
    print(dem_ds.rio.crs)
    minx = float(dem_ds.x.min())
    miny = float(dem_ds.y.min())
    maxx = float(dem_ds.x.max())
    maxy = float(dem_ds.y.max())
    print(minx, miny, maxx, maxy)

# %% [markdown]
# ## Download and preprocess Sentinel 2 true colour imagery
#
# Using relatively cloud-free imagery taken on 9 Nov 2021.
# Data search was done using EO Browser. Link is at
# https://apps.sentinel-hub.com/eo-browser/?zoom=13&lat=-77.84769&lng=166.7601&themeId=DEFAULT-THEME&visualizationUrl=https%3A%2F%2Fservices.sentinel-hub.com%2Fogc%2Fwms%2F42924c6c-257a-4d04-9b8e-36387513a99c&datasetId=S2L1C&fromTime=2021-11-09T00%3A00%3A00.000Z&toTime=2021-11-09T23%3A59%3A59.999Z&layerId=1_TRUE_COLOR
#
# The AWS URLs were discovered using intake-stac.
# I've omitted the code for brevity, but you can follow
# https://github.com/intake/intake-stac/blob/0.3.0/examples/aws-earth-search.ipynb
# to find out how the links to the Cloud Optimized GeoTiff files are obtained.

# %%
band4 = rioxarray.open_rasterio(
    filename="https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/58/C/EU/2021/11/S2B_58CEU_20211109_0_L2A/B04.tif",
    masked=True,
)
band4["band"] = 4 * band4.band
band3 = rioxarray.open_rasterio(
    filename="https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/58/C/EU/2021/11/S2B_58CEU_20211109_0_L2A/B03.tif",
    masked=True,
)
band3["band"] = 3 * band3.band
band2 = rioxarray.open_rasterio(
    filename="https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/58/C/EU/2021/11/S2B_58CEU_20211109_0_L2A/B02.tif",
    masked=True,
)
band2["band"] = 2 * band2.band

# %%
# Stack the Red (4), Green (3) and Blue (2) bands together
band432 = xr.concat(objs=[band4, band3, band2], dim="band")

# %%
# Reproject image from EPSG:32758 to EPSG:3294
band432_reprojected = band432.rio.reproject(dst_crs="EPSG:3294")

# %%
# Clip Sentinel 2 imagery to geographical extent of the DEM
b432 = band432_reprojected.rio.clip_box(minx=minx, miny=miny, maxx=maxx, maxy=maxy)

# %%
# Normalize from 16-bit to 8-bit colors
b432_scott_base = ((b432 - b432.min()) / (b432.max() - b432.min())) * 2 ** 8

# %%
# Save preprocessed Sentinel 2 image to a GeoTIFF file
b432_scott_base.rio.to_raster(raster_path="B432_3294.tif", dtype="uint8")

# %%
# Inspect the GeoTIFF file's metadata
print(pygmt.grdinfo(grid="B432_3294.tif"))

# %% [raw]
# # If you want to download the actual GeoTIFF directly
# for band in ["B04", "B03", "B02"]:
#     pygmt.which(
#         fname=f"https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/58/C/EU/2021/11/S2B_58CEU_20211109_0_L2A/{band}.tif",
#         download=True,
#     )

# %% [markdown]
# Now for the colour plot! We'll use PyGMT's
# [`grdview`](https://www.pygmt.org/v0.5.0/api/generated/pygmt.Figure.grdview.html)
# function to make a perspective view plot in 3D. The DEM is used as the relief
# grid, and draped on top is the satellite imagery.

# %%
fig = pygmt.Figure()
with pygmt.config(PS_PAGE_COLOR="#a9aba5"):
    fig.grdview(
        grid="Mcmd.tif",  # DEM layer
        drapegrid="B432_3294.tif",  # Sentinel2 image layer
        surftype="i600",  # image draping with 600dpi resolution
        perspective=[170, 20],  # view azimuth and angle
        zscale="0.005",  # vertical exaggeration
        # frame="af",
    )
fig.savefig(fname="day11_3d.png")
fig.show()
