

import os
import rasterio
import rasterio.mask
import geopandas as gpd
from os.path import dirname as up
import numpy as np


def crop_boundary(intif, inbound):

    with rasterio.open(intif) as src:
        out_image, out_transform = rasterio.mask.mask(src, inbound, crop=True)
        out_meta = src.meta

    out_meta.update({"driver": "GTiff",
                     "height": out_image.shape[1],
                     "width": out_image.shape[2],
                     "transform": out_transform})

    return out_meta, out_image


root_path = os.path.abspath('..')
study_area = os.path.join(root_path, 'data/PoquosonBound.geojson')
dem_file = "L://CBTBDEM_v2//Chesapeake_Bay_Topobathy_DEM_1m_v2.tif"

gdf = gpd.read_file(study_area)
shapes = [gdf.geometry[0]]

meta, img_array = crop_boundary(dem_file, shapes)

# low: between mlw and mhw -0.432, 0.259
# high: 1.5 tide
img_array = img_array[0]

mlw = -0.432
mhw = 0.259
uppder = mhw + (mhw - mlw)/2

img_array = np.where((img_array >=-mlw) & (img_array <= mhw), 2, img_array)
img_array = np.where((img_array > mhw) & (img_array <= uppder), 1, img_array)
img_array = np.where((img_array == 1) | (img_array == 2), img_array, 0)

poquoson_marsh = os.path.join(root_path, 'outputs/poquoson_marsh.tif')

with rasterio.open(poquoson_marsh, "w", **meta) as dest:
    dest.write(img_array, 1)


