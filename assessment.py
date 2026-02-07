#Required packages
import json
import openeo
from openeo.processes import array_interpolate_linear
import numpy as np

import rasterio
from rasterio.mask import mask
from rasterio.warp import reproject, Resampling
from shapely.geometry import shape

def generate_dekadal_ndvi(aoi_path, start_date, end_date, output_filename):
    # Establishing connection to CDSE with openEO
    conn = openeo.connect("https://openeo.dataspace.copernicus.eu")
    conn.authenticate_oidc()

    # Load the given AOI must be in data folder
    with open(aoi_path) as f:
        aoi_geojson = json.load(f)

    # Load collection based on aoi and given spatial extend
    s2 = conn.load_collection(
        "SENTINEL2_L2A",
        spatial_extent=aoi_geojson,
        temporal_extent=[start_date, end_date],
        bands=["B04", "B08", "SCL"]
    )

    # Integers to reflectivity
    red = s2.band("B04") / 10000.0
    nir = s2.band("B08") / 10000.0
    scl = s2.band("SCL")

    # Mask clouds from the categorical SCL 8, 9, 10 from https://custom-scripts.sentinel-hub.com/custom-scripts/sentinel-2/scene-classification/
    cloud_mask = (scl == 8) | (scl == 9) | (scl == 10)
    valid_mask = ~cloud_mask
    valid_mask_10m = valid_mask.resample_cube_spatial(red)

    # Apply mask
    red_masked = red.mask(valid_mask_10m)
    nir_masked = nir.mask(valid_mask_10m)

    # Compute NDVI add a tiny number to avoid division with 0
    ndvi_s2 = (nir_masked - red_masked) / (nir_masked + red_masked + 1e-6)
	
    # create 10-daily composites ---> .aggregate_temporal_period and apply linear interpolation ---> .apply_dimension to avoid gaps
    ndvi_s2 = ndvi_s2.aggregate_temporal_period("dekad", reducer="median").apply_dimension(dimension="t", process="array_interpolate_linear")
	
    if output_filename.endswith(".tif") or output_filename.endswith(".tiff"):
        ndvi_s2.download(output_filename, format="GTiff")
    elif output_filename.endswith(".nc"):
        ndvi_s2.download(output_filename, format="NetCDF")
    else:
        raise ValueError("Supported filenames end with: .tif, .tiff or .nc")
	
# Call the function
generate_dekadal_ndvi(
    aoi_path="data/aoi.json",
    start_date="2025-08-01",
    end_date="2025-08-31",
    output_filename="ndvi_dekadal_august_2025_.tif"
)
# ---------------------------------------------------------
#optional part
aoi_path = "data/aoi.json"                  
clms_path = "global_median_ndvi.tiff"              
dekadal_ndvi_path = "ndvi_dekadal_august_2025_.tif"
output_filled_path = "ndvi_dekadal_august_2025__filled.tif"

with open(aoi_path) as f:
    aoi_geojson = json.load(f)

geoms = [shape(aoi_geojson)]

with rasterio.open(clms_path) as src:
    clms_clipped, clms_transform = mask(src, geoms, crop=True)
    clms_meta = src.meta.copy()

clms_meta.update({
    "height": clms_clipped.shape[1],
    "width":  clms_clipped.shape[2],
    "transform": clms_transform
})

# NDVI fixed scaling factor of 1/250 with an offset of –0.08
#from https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/clms/bio-geophysical-parameters/vegetation/vegetation-indices/ndvi_global_300m_10daily_v2.html
# ---------------------------------------------------------
clms_scaled = clms_clipped.astype("float32") / 250.0 - 0.08

# Resampling global ndvi to 10m
with rasterio.open(dekadal_ndvi_path) as ndvi_src:
    target_meta = ndvi_src.meta.copy()
    target_arr = ndvi_src.read(1)

clms_resampled = np.zeros_like(target_arr, dtype=np.float32)

reproject(
    source=clms_scaled[0],
    destination=clms_resampled,
    src_transform=clms_transform,
    src_crs=clms_meta["crs"],
    dst_transform=target_meta["transform"],
    dst_crs=target_meta["crs"],
    resampling=Resampling.bilinear
)

NDVI_NODATA = target_meta.get("nodata") #tif flag for no data - after inspection

#Collecting the holes both nodata and Nan if exist
holes = (target_arr == NDVI_NODATA) | np.isnan(target_arr)

filled = target_arr.copy()
filled[holes] = clms_resampled[holes]

target_meta.update(dtype="float32")

with rasterio.open(output_filled_path, "w", **target_meta) as dst:
    dst.write(filled.astype("float32"), 1)
