# 10-daily NDVI composite with openeo and python Repository
### Part 1
This repo utilizes the **openEO API** to compute a 10-daily NDVI composite product from Sentinel-2 L2A data for a given date-range and AOI.
Since satellite revisits are irregular, an interpolation method is implemented to produce data on exactly the 1st, 11th, and 21st of each month (the
standard CLMS dekadal grid).

The script performs cloud-masking utilizing the [Scene Classification](https://custom-scripts.sentinel-hub.com/custom-scripts/sentinel-2/scene-classification/) Layer (SCL) layer and excludes pixels with:
- Cloud medium probability
- Cloud high probability
- Thin cirrus

Moreover, the script utilizes the `ndvi_global_300m_10daily_v3` product to fill remaining data gaps in the 10-daily NDVI composite 

#### The repository includes
- The `assessment.py` which is the python script that contains all the logic
- A folder called 'data', in which there is the file `aoi.json` that contains the geometry of the area of interest and it is used to limit our spatial extend
- This Readme.md file that contains further specifications and instructions on how to run the `assessment.py`
- A link to a conceptual workflow expalining the overall process to onboard data efficiently using the Sentinel Hub BYOC API (see Part 2 at the end of readme)

# Other Specifications - To run this script you need:
- [Git](https://git-scm.com/install/) & a GitHub account
- Access to Anaconda prompt. A ligther version of Anaconda is [Miniconda](https://www.anaconda.com/docs/getting-started/miniconda/main)
- An account in CDSE
- To be logged in the [Sentinel Browser](https://browser.dataspace.copernicus.eu/?zoom=5&lat=50.14875&lng=20.78613&themeId=DEFAULT-THEME&visualizationUrl=U2FsdGVkX1%2B2VejemOuCIwdo1Phlva9%2BkG73C62wtZA5uGiujkpcwM9B6bLkBw9p7CMsx7dVEYlEneQcMvIKppUH6oBhTbJyiRoSjN5MVbR48BgQQAPl6TorIkTf%2FX%2FO&datasetId=COPERNICUS_CLMS_NDVI_300M_10DAILY_V3&fromTime=2025-08-11T00%3A00%3A00.000Z&toTime=2025-08-11T23%3A59%3A59.999Z&layerId=NDVI&demSource3D=%22MAPZEN%22&cloudCoverage=30&dateMode=SINGLE&clmsSelectedPath=COPERNICUS_CLMS_NDVI_300M_10DAILY_V3&clmsSelectedCollection=COPERNICUS_CLMS_NDVI_300M_10DAILY_V3)
or use the generated token and confirm identity
- Since the Copernicus Land Monitoring Service (CLMS) - CLMS 300m product **is not exposed via the openEO API**, to run this code successfuly the user needs to:
  - **Manually download** the file `c_gls_NDVI300_202508110000_GLOBE_OLCI_V3.0.1_cog` from the [Sentinel Browser](link.dataspace.copernicus.eu/0ytz)
  - Save it as "global_ndvi.tiff" **in the same folder where the script exists**. This file does not exists in this repository.
- Inside the same folder with the script, a subfolder called 'data' should exists which contains the aoi.json. This is included in the repository
- The `.yml` file is an **exact copy** (including python version) of the environment where the script was created and it will be used to create a clone-environment via Anaconda prompt

- To parametrize the function please modify lines 57-61:
  ```
  generate_dekadal_ndvi_with_clms(
      aoi_path="data/aoi.json",
      start_date="2025-08-01",
      end_date="2025-08-31",
      output_filename="ndvi_dekadal_august_2025_.tif"
  )
  ```
  - The user can specify the output filename but the format (ending) **should be explicitly defined**. **Only .nc, .tiff and .tif formats are supported**.
# How to run the script
- Clone the repository in your preferable path using `git clone https://github.com/eleni-tkm/geospatial-ndvi.git` using GitBash
- Open Anaconda Prompt 
- Type: `conda env create -f path\to\environment.yml --name <NameOfYourEnvironment>`
- Activate your environment with `conda activate <NameOfYourEnvironment>`
- Cd to the folder in your PC that contains the clone of the repository `cd path\to\assessment.py`
- Type `python assessment.py`

## Warning!
If this error occurs: 
```
  Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    File "C:\Users\..\Anaconda3\envs\NameOfYourEnvironment\lib\site-packages\rasterio\__init__.py", line 22, in <module>
      from rasterio._base import gdal_version
  ImportError: DLL load failed: The specified module could not be found.
```
There is propably a conflict between the system's gdal version that the user has in the system path and the gdal version of the environment

- To confirm, type inside your environment:
`where gdal*.dll`
Output:
```
C:\Users\...\anaconda3\envs\NameOfYourEnvironment\Library\bin\gdal.dll
C:\Users\...\AppData\Local\Programs\OSGeo4W\bin\gdal312.dll <--this should not exist
```
- To fix, type inside your environment:
`set "PATH=%PATH:C:\Users\...\AppData\Local\Programs\OSGeo4W\bin;=%"` . This will **temporarily** remove the OSGeo4W bin directory from PATH for the current shell session only!

Now you can run the script.

# Outputs
If the function call remain as it is the outputs should be:
- `ndvi_dekadal_august_2025_.tif`: a 10-daily NDVI composite product from Sentinel-2 L2A limited temporaly by `"2025-08-01" - "2025-08-31"` and limited spatially by the `aoi.json`
- `ndvi_dekadal_august_2025__filled.tif`: a 10-daily NDVI composite product from Sentinel-2 L2A limited temporaly by `"2025-08-01" - "2025-08-31"`, limited spatially by the `aoi.json` and gap-filled by a CLMS product (Dataset: `ndvi_global_300m_10daily_v3)

### Part 2
Part 2 includes a conceptual workflow describing the steps to onboard data efficiently using the Sentinel Hub BYOC API. The link was created using [Canva](https://www.canva.com/)
You can find the workflow [here](https://www.canva.com/design/DAHApMHdwdk/8I58NmAHh-QdGZAbVoC_RQ/view?utm_content=DAHApMHdwdk&utm_campaign=designshare&utm_medium=link2&utm_source=uniquelinks&utlId=h0935883c7f).

# Further Improvements
- Use an API where CLMS is available to utilize only a CDSE API without external packages for gap filling
- Add exceptions for example if the "global_ndvi.tiff" does not exists
- Write both parts in one file
- Further code improving and formatting
- Add sanity tests (visualize the data, print statistics)
- More detailed workflow that also mentions specific tools

