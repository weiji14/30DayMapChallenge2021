# Day 14 : Map with new tool

As the whole #30DayMapChallenge is much about learning and experimenting,
this day is dedicated to exploring new tools! So no PyGMT for today, but we'll
still be using satellite Earth Observation data, this time, to make a timelapse
GIF of an iceberg calving from Antarctica!

Sentinel Hub is running a parallel challenge this November 2021, so let's take
their [EO Browser](https://www.sentinel-hub.com/explore/eobrowser) for a spin.

[![Sentinel Hub Twitter Challenge - November 2021](https://user-images.githubusercontent.com/23487320/141668808-8ff644de-0032-45c2-906d-db1671f371d3.png)](https://www.sentinel-hub.com/develop/community/twitter-challenge-nov-2021)

## Part 1: Discover Sentinel 1 images

1. Go to https://apps.sentinel-hub.com/eo-browser. You'll need to login or
   create an account first to get the timelapse functionality to work.
2. Take your time to pan around the map and find an area you want to explore.
   I'll be heading to the Brunt Ice Shelf in Antarctica for this exercise.
3. On the left panel, click on the 'Discover' tab, where you can search for
   data sources from different satellites like the Sentinel and Landsat series.
4. Since we don't want to mess with clouds, let's go with Sentinel 1 which is a
   satellite that carries a Synthetic Aperture Radar (C-band) sensor. We'll
   just go into the Advanced Settings and tick the box for EW - Extra-Wide
   Swath and HH+HV polarization. This filter will work well for our iceberg
   calving study area in Antarctica.

   ![EO Browser Discover tab](https://user-images.githubusercontent.com/23487320/141668780-a7ab46e1-1cfc-4547-8fc7-e5c4fe1109e7.png)

5. Next, scroll down to the very bottom. You can optionally select a time range
   [UTC], or just click 'Search'. I chose dates from 2021-01-01 to 2021-11-14.
6. You should be taken to a view like below. On the left panel, there is a list
   of Sentinel-1 images taken on different dates. The map on the right will
   show half transparent blue 'tiles' which you can click on, and that would
   give you a list of images for that geographical area.

   ![EO Browser User Interface](https://user-images.githubusercontent.com/23487320/141669158-99da321b-0435-48b5-a5c4-6c594987c64d.png)

7. Clicking on the 'Visualize' button will take us to the next step. I'm just
   going to click on one of the blue tiles on the lower left (the blue tile
   will turn green when you hover over), and there will be a pop up with a
   shortlist of Sentinel-1 images. I then selected the first image on the list
   which was taken on 2021-11-03.

   ![EO Browser pop up](https://user-images.githubusercontent.com/23487320/141669734-1e04dd94-146f-4905-b821-0a6109fceccd.png)


## Part 2: Visualize Sentinel-1 images

1. On the left panel, you should now be on the 'Visualize' tab. If you want to
   follow along, go to https://sentinelshare.page.link/XAFa
2. There will be a few options for Sentinel-1 polarization to choose from, have
   a play around to see what each of them looks like. I'll just go for the
   'HH - decibel gamma0 - orthorectified' visualization option.

   ![Sentinel-1 visualization options](https://user-images.githubusercontent.com/23487320/141669961-7ee4fd01-3fb8-4efe-b59c-028889284ea9.png)

3. If you want to look at another Sentinel-1 image from a different location
   or time, click on the 'Discover' tab on the left panel, and that should take
   you back to the original list you searched for. Now is a good time to get an
   idea of how things looks like over time.
4. Once you've got a good picture of the area, and decided on the geographical
   extent you want to map, it's time to move to the next step.


## Part 3: Producing the timelapse GIF animation

1. Ensure that you have logged in, and there should be a button on the right
   toolbar with a film logo that is used for creating timelapse animations.

  ![Button to create timelapse](https://user-images.githubusercontent.com/23487320/141670103-05d58b9f-118a-4ec7-b8a5-102d714e511a.png)

2. Clicking on that film button will show a half transparent blue pop-up in the
   middle of the map with the words 'Create a timelapse of this area' and a
   round blue 'Play' button in the middle. Pan and/or zoom around the map, and
   decide on a good region for your timelapse before clicking on the blue
   'Play' button.

   ![Ready to make a timelapse](https://user-images.githubusercontent.com/23487320/141670165-59ead720-373f-4654-b168-d809b60d985f.png)

3. You should now see a 'Timelapse' window pop-up. There are a few options on
   the left to choose such as the date range, and the desired frequency of
   images. I picked dates from 2021-01-01 to 2021-11-14, and a '1 image per
   day' frequency. You want want to pick 'week' or 'month' for longer time
   periods. Click on the Search button when you're done.

   ![Timelapse options](https://user-images.githubusercontent.com/23487320/141670277-447d2d33-08b8-4288-b71b-b7a5dde12b8b.png)

4. Now, there should be a list of more than a hundred Sentinel-1 images. Not
   all of the images are good quality, so I recommend going through the list
   and deselect those that are mostly dark (i.e. contain NaN values), so that
   the animation looks nicer later on. Below is an example of an image you
   probably don't want.

   ![An mostly dark image with NaN values](https://user-images.githubusercontent.com/23487320/141670370-ddafb23b-0942-4b01-a7d1-40da10e900c6.png)

5. Next, you can preview the animation by clicking on the Play button and set
   the number of frames per second (e.g. 10).

   ![image](https://user-images.githubusercontent.com/23487320/141670418-b8dbfb4d-7f24-4a2e-b69f-ca6bc197f0a7.png)

6. Once you're happy with how the animated preview looks, click on the Download
   button on the bottom right, give it a few minutes, and you're all done!


### Part 4: Optimizing GIF file size (optional)

Since GIFs have an upload file size limit for Twitter (15MB),
it was necessary to reduce the 22MB output to something smaller.
Following https://legacy.imagemagick.org/Usage/anim_opt/#compress_opt,
we can use ImageMagick to do some transparency optimization:

    convert S1_AWS_EW_HH-timelapse.gif -layers OptimizeTransparency +map S1_AWS_EW_HH-timelapse_opttransp.gif

This brings the size from 22MB down to 14MB, enough for Twitter.

Note that GitHub has a file size limit of 10MB, and it is possible to use
`gifsicle`'s LZW Optimization to bring the GIF size down even more (but the
results start looking a lot worse). As an alternative, you could try:

    gifsicle -i S1_AWS_EW_HH-timelapse.gif --optimize=3 --colors 32 --output S1_AWS_EW_HH-timelapse_lzwcompress.gif

This decreases the size from 22MB down to 7.9MB, but the colors won't look as
nice, so I'd use it as a last resort. This suggestion was based on
https://superuser.com/questions/1107200/optimize-animated-gif-size-in-command-line


### Notes

Here's a list of references about Iceberg A-74:

- https://en.wikipedia.org/wiki/Iceberg_A-74
- https://phys.org/news/2021-02-brunt-ice-shelf-brink.html
- https://phys.org/news/2021-08-a-iceberg-collision-brunt-ice.html

There have been several other iceberg calving events in the past,
the Larsen C was another famous one, here are the links:

- https://en.wikipedia.org/wiki/Larsen_Ice_Shelf#Larsen_C
- https://apps.sentinel-hub.com/eo-browser/?zoom=6&lat=-67.81339&lng=-65.23682&themeId=DEFAULT-THEME&visualizationUrl=https%3A%2F%2Fservices.sentinel-hub.com%2Fogc%2Fwms%2F694b409a-e12b-4922-8d51-c28dc12c8474&datasetId=S1_AWS_EW_HHHV&fromTime=2021-11-13T00%3A00%3A00.000Z&toTime=2021-11-13T23%3A59%3A59.999Z&layerId=EW-DH-HV-DECIBEL-GAMMA0-RADIOMETRIC-TERRAIN-CORRECTED
