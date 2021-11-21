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
# # Day 20 : Movement
#
# Visualizing movement can be done with a static map or with an animation.

# %%
import asyncio
import os
import glob

import aioftp
import pandas as pd

loop = asyncio.get_event_loop()

# %% [markdown] tags=[]
# # Download Himawari-8 imagery
#
# Let's look at some weather over Southeast-Asia from
# 11 Oct 2021 to 13 Oct 2021 when
# [Tropical Cyclone Kompasu](https://en.wikipedia.org/wiki/Tropical_Storm_Kompasu_(2021))
# (Maring) struck the Phillipines, Taiwan and parts of southern China.
# We'll use far-infrared imagery from the
# [Himawari-8 satellite](https://en.wikipedia.org/wiki/Himawari_8).
# This satellite takes an image of the Asia-Pacific region every
# 10 minutes, but we'll just download an image every hour to save
# on space and processing time.
#
# - User guide: https://www.eorc.jaxa.jp/ptree/userguide.html
# - Real-time viewer: https://himawari8.nict.go.jp
#
# Useful references:
# - https://quicklooks.cr.chiba-u.ac.jp/~himawari_movie/rd_gridded.html
# - https://github.com/gSasikala/ftp-himawari8-hsd

# %%
# Get times from 2021 Oct 11 to 2021 Oct 13, every 1 hour
datetimes = pd.date_range(start="20211011T12:00:00", end="20211013T12:00:00", freq="1H")
print(f"Total number of files to download:{len(datetimes)}")

# %%
filepaths: list = []
for dt in datetimes:
    # Get path to file on FTP server. Example path look like
    # 'jma/netcdf/202110/13/NC_H08_20211013_0000_R21_FLDK.06001_06001.nc'
    folder = f"jma/netcdf/{dt.year}{dt.month:02d}/{dt.day:02d}"
    filename = f"NC_H08_{dt.year}{dt.month:02d}{dt.day:02d}_{dt.hour:02d}{dt.minute:02d}_R21_FLDK.06001_06001.nc"
    filepath = os.path.join(folder, filename)
    filepaths.append(filepath)

# %%
async def get_himawari(path: str):
    if not os.path.exists(path=os.path.basename(path)):
        async with aioftp.Client.context(
            host="ftp.ptree.jaxa.jp", user="user_domain.com", password="abcdefgh"
        ) as client:
            await client.download(path)


# %%
async def main():
    tasks = [asyncio.create_task(coro=get_himawari(filepath)) for filepath in filepaths]
    await asyncio.wait(fs=tasks)


# %%
# Download NetCDF files from FTP server asynchronously
asyncio.run_coroutine_threadsafe(coro=main(), loop=loop)

# %%
# Check that downloaded number of files is as expected
# !ls -lh NC_H08_*.nc | wc -l
assert len(glob.glob("NC_H08_*.nc")) == len(datetimes)

# %% [markdown]
# ## Make the GIF animation!
#
# Let's use GMT's [movie](https://docs.generic-mapping-tools.org/6.2/movie.html)
# command to make the GIF animation. We'll plot Himawari-8's Band 13 (Far Infrared)
# on top of the Black Marble (earth_night) imagery. The map will also include
# longitude/latitude gridlines and a text annotation of the image's capture time.

# %%
%%file typhoon_kompasu.sh
gmt begin
    # Get datetime in format YYYYMMDD_hhmm, e.g. 20121011_1800
    datetime=$(date --date=$(gmt math -T2021-10-11T12:00:00/2021-10-13T12:00:00/1h -o0 -qo${MOVIE_FRAME} T =) "+%Y%m%d_%H%M")

    # pygmt.config(FONT_ANNOT="white", MAP_FRAME_TYPE="inside", PS_PAGE_COLOR="black")
    gmt set FONT_ANNOT=white
    gmt set MAP_FRAME_TYPE=inside
    gmt set PS_PAGE_COLOR=black

    # fig.shift_origin(xshift="f0", yshift="f0")
    gmt plot -T -Xf0 -Yf0

    # fig.grdimage(grid="@earth_night_30m", region="90/140/5/35", projection=EPSG:32651", frame=True)
    gmt grdimage @earth_night_30m -R90/140/5/35 -JU50Q/${MOVIE_WIDTH} -BwSnE -Bafg

    # fig.grdimage(grid='NC_H08_20211011_1200_R21_FLDK.06001_06001.nc?tbb_13', cmap="gray", transparency=50)
    gmt grdimage NC_H08_${datetime}_R21_FLDK.06001_06001.nc?tbb_13 -Cgray -t50 -Ve

    # fig.text(text=datetime, position="TC", offset="0c/-2c")
    echo ${datetime} | gmt text -F+cTC -D0c/-2c
gmt end

# %%
# movie(canvassize="540p", nframes=49, displayrate=3, format="gif", prefix="day20_movement", erase=True)
!gmt movie typhoon_kompasu.sh -C480p -T49 -D3 -A+l -Nday20_movement -Z

# %% [markdown]
# ## (Optional) Processing using xarray/PyGMT
#
# For reference, this was some experimental code on
# reading Himawari-8 NetCDF files using `xarray`,
# and doing the plotting of a single map using `PyGMT`.

# %%
import pygmt
import rioxarray
import xarray as xr

# %%
for dt in datetimes:
    filename = f"NC_H08_{dt.year}{dt.month:02d}{dt.day:02d}_{dt.hour:02d}{dt.minute:02d}_R21_FLDK.06001_06001.nc"
    print(f"Processing {filename}")

    # Process the Himawari-8 data using xarray/rioxarray
    with xr.open_dataset(filename_or_obj=filename) as ds:
        # Crop to SouthEast Asia region
        ds_SEA: xr.Dataset = ds.sel(longitude=slice(90, 140), latitude=slice(35, 5))

        # Get Red, Green and Blue only
        ds_SEA_RGB: xr.DataArray = xr.concat(
            objs=[ds_SEA.albedo_03, ds_SEA.albedo_02, ds_SEA.albedo_01],
            dim="band",
        )

        # Apply coordinate reference system
        ds_SEA_RGB.rio.set_crs(input_crs="EPSG:4326")
        ds_SEA_RGB = ds_SEA_RGB.rio.reproject(dst_crs="EPSG:4326")

        # Save 8-bit data to GeoTIFF
        raster_path: str = f"TIF_H08_{dt.year}{dt.month:02d}{dt.day:02d}_{dt.hour:02d}{dt.minute:02d}.tif"
        (ds_SEA_RGB * 2 ** 8).rio.to_raster(raster_path=raster_path, dtype="uint8")

    # os.remove(path=filename)  # Remove original NetCDF file to save space
    # break

# %%
# Inspect the GeoTIFF file's metadata
print(pygmt.grdinfo("TIF_H08_20211011_1200.tif"))

# %%
# Plot the map!
fig = pygmt.Figure()
fig.grdimage(
    grid="@earth_night_30m", region="100/130/5/30", projection="EPSG:32651", frame=True
)
fig.grdimage(
    grid="NC_H08_20211011_1200_R21_FLDK.06001_06001.nc?tbb_13",
    cmap="gray",
    transparency=50,
)
fig.colorbar()
fig.show()
