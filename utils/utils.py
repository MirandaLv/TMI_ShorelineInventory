

import rasterio
import os
from rasterio.enums import Resampling
import rasterio
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

def upsample(source_path, target_path, method=Resampling.bilinear):

    """
    img_lres_path: low resolution cropped band path
    img_hres_path: high resolution cropped band path
    img_size: the size to resample
    outf: output resampled Bands
    """

    dataset_source = rasterio.open(target_path)
    # target_res_w, target_res_h = dataset_source.res

    dataset = rasterio.open(source_path)

    # resample data to target shape
    data = dataset.read(
        out_shape=(
            dataset.count,
            int(dataset_source.width),
            int(dataset_source.height)
        ),
        resampling=method
    )

    meta = dataset_source.meta
    meta['count'] = dataset.count

    return meta, data

