
import os
import sys
root_path = os.path.abspath('..')
sys.path.append(root_path)
import rasterio
import rasterio.mask
import geopandas as gpd
from os.path import dirname as up
import numpy as np
from utils import utils


study_area = os.path.join(root_path, 'data/island_proj.geojson')
dem_file = "L://CBTBDEM_v2//Chesapeake_Bay_Topobathy_DEM_1m_v2.tif"

# Step 1. Masking the DEM with the county boundary.
gdf = gpd.read_file(study_area)
shapes = [gdf.geometry[0]]
meta, img_array = utils.crop_boundary(dem_file, shapes)

poquoson_dem = os.path.join(root_path, 'outputs/island_dem.tif')

with rasterio.open(poquoson_dem, "w", **meta) as dest:
    dest.write(img_array)


# Step 2. Resampling the Poquoson DEM so the resolution and dimension is the same with NAIP output
# and Reclassify the outputs to high/low marsh based on the thresholds.

# low: between mlw and mhw -0.432, 0.259
# high: 1.5 tide
# resampled_dem = resampled_dem[0]

ml_predict_NAIP = os.path.join(up(up(root_path)), 'projects/NewTMI_poquoson/island2_prediction_smooth_sentinel.tif')
poquoson_reclass = os.path.join(root_path, 'outputs/island_dem_reclassed.tif')

resampled_meta, resampled_dem = utils.upsample(poquoson_dem, ml_predict_NAIP)

mlw = -0.432
mhw = 0.259
upper = mhw + (mhw - mlw)/2

resampled_dem = np.where(resampled_dem > mhw, 1, resampled_dem)
resampled_dem = np.where((resampled_dem >= mlw) & (resampled_dem <= mhw), 2, resampled_dem)
resampled_dem = np.where((resampled_dem == 1) | (resampled_dem == 2), resampled_dem, -1).astype(int)

with rasterio.open(poquoson_reclass, "w", **resampled_meta) as dest:
    dest.write(resampled_dem)



# Step 4. Masking the reclassed DEM marsh types with binary marsh prediction from NAIP
poquoson_reclass = os.path.join(root_path, 'outputs/island_dem_reclassed.tif')
poquoson_out = os.path.join(root_path, 'outputs/island_combined.tif')

ml_predict_array = rasterio.open(ml_predict_NAIP).read(1)
ml_predict_array = np.where((ml_predict_array==1) | (ml_predict_array==2), 1, 0)

poquoson_reclass_array = rasterio.open(poquoson_reclass).read(1)
masked_out = np.multiply(ml_predict_array, poquoson_reclass_array)

with rasterio.open(poquoson_out, "w", **resampled_meta) as dest:
    dest.write(masked_out, 1)



