#Required packages
import json
import openeo
from openeo.processes import array_interpolate_linear


def generate_dekadal_ndvi_with_clms(aoi_path, start_date, end_date):
    # Establishing connection to CDSE with openEO
    conn = openeo.connect("https://openeofed.dataspace.copernicus.eu").authenticate_oidc()

    # Load the given AOI must be in data folder
    with open(aoi_path) as f:
        aoi_geojson = json.load(f)

    # Load collections based on aoi and given spatial extend
    s2 = conn.load_collection(
        "SENTINEL2_L2A",
        spatial_extent=aoi_geojson,
        temporal_extent=[start_date, end_date],
        bands=["B04", "B08", "SCL"]
       ) 

    # Scale red/NIR to 0–1 (integers to reflectivity)
    red = s2.band("B04") / 10000.0
    nir = s2.band("B08") / 10000.0
    scl = s2.band("SCL")

    # Mask clouds from the categorical SCL 3, 6, 8, 9, 10
    cloud_mask = (scl == 8) | (scl == 9) | (scl == 10) | (scl == 3) | (scl == 6)
    valid_mask = ~cloud_mask
    valid_mask_10m = valid_mask.resample_cube_spatial(red)

    # Apply mask
    red_masked = red.mask(valid_mask_10m)
    nir_masked = nir.mask(valid_mask_10m)

    # Compute NDVI add a tiny number to avoid division with 0
    ndvi_s2 = (nir_masked - red_masked) / (nir_masked + red_masked + 1e-6)
	
    # create 10-daily composites ---> .aggregate_temporal_period and apply linear interpolation ---> .apply_dimension to avoid gaps
    ndvi_s2 = ndvi_s2.aggregate_temporal_period("dekad", reducer="median").apply_dimension(dimension="t", process="array_interpolate_linear")
    
    job = ndvi_s2.create_job(
        out_format="GTiff",
        title="Dekadal NDVI"
    )

    job.start_and_wait()
    job.get_results().download_files(r"C:\Users\HP-122024\Desktop\assessment")
	
# Call the function
generate_dekadal_ndvi_with_clms(
    aoi_path="data/aoi.json",
    start_date="2025-08-01",
    end_date="2025-08-31",
)
