# 10‑daily NDVI composite products with openEO and Python
### Part 1
This repo utilizes the **openEO API** and introduces a **cloud‑native geospatial workflow** to compute 10‑daily NDVI composite products from Sentinel‑2 L2A data for a given date range and AOI.
Since satellite revisits are irregular, an interpolation method is implemented to produce data on exactly the 1st, 11th, and 21st of each month (the
standard CLMS dekadal grid).

The script performs cloud-masking utilizing the [Scene Classification](https://custom-scripts.sentinel-hub.com/custom-scripts/sentinel-2/scene-classification/) Layer (SCL) layer and excludes pixels with:
- Cloud medium probability
- Cloud high probability
- Thin cirrus
- Cloud shadows and,
- Water


#### The repository includes
- The `dekadal-ndvi.py` which is the python script that contains all the logic
- A folder called `'data'`, in which there is the file `aoi.json` that contains the geometry of the area of interest and it is used to limit our spatial extend
- This `README.md` file that contains further specifications and instructions on how to run the `dekadal-ndvi.py`
- A link to a conceptual workflow expalining the overall process to onboard data efficiently using the Sentinel Hub BYOC API (see Part 2 at the end of `README.md`)

# Other Specifications - To run this script you need:
- [Git](https://git-scm.com/install/) & a GitHub account
- Access to Anaconda prompt. A ligther version of Anaconda is [Miniconda](https://www.anaconda.com/docs/getting-started/miniconda/main)
- An account in CDSE
- To be logged in the [Sentinel Browser](https://browser.dataspace.copernicus.eu/?zoom=5&lat=50.14875&lng=20.78613&themeId=DEFAULT-THEME&visualizationUrl=U2FsdGVkX1%2B2VejemOuCIwdo1Phlva9%2BkG73C62wtZA5uGiujkpcwM9B6bLkBw9p7CMsx7dVEYlEneQcMvIKppUH6oBhTbJyiRoSjN5MVbR48BgQQAPl6TorIkTf%2FX%2FO&datasetId=COPERNICUS_CLMS_NDVI_300M_10DAILY_V3&fromTime=2025-08-11T00%3A00%3A00.000Z&toTime=2025-08-11T23%3A59%3A59.999Z&layerId=NDVI&demSource3D=%22MAPZEN%22&cloudCoverage=30&dateMode=SINGLE&clmsSelectedPath=COPERNICUS_CLMS_NDVI_300M_10DAILY_V3&clmsSelectedCollection=COPERNICUS_CLMS_NDVI_300M_10DAILY_V3) - or use the generated token and confirm identity
- Inside the same folder with the script, a subfolder called `'data'` should exists which contains the `aoi.json`. This is included in the repository
- The `.yml` file is an **exact copy** (including python version) of the environment where the script was created and it will be used to create a clone-environment via Anaconda prompt

- To parametrize the function please modify lines 57-61:
  ```
  generate_dekadal_ndvi(
      aoi_path="data/aoi.json",
      start_date="2025-07-24",
      end_date="2025-08-31",
  )
  ```

# How to run the script
- Clone the repository in your preferable path using `git clone https://github.com/eleni-tkm/geospatial-ndvi.git` using GitBash
- Open Anaconda Prompt 
- Type: `conda env create -f path\to\environment.yml --name <NameOfYourEnvironment>`
- Activate your environment with `conda activate <NameOfYourEnvironment>`
- Cd to the folder in your PC that contains the clone of the repository `cd path\to\dekadal-ndvi.py`
- Type `python dekadal-ndvi.py`

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

- To confirm, type inside your environment: `where gdal*.dll`
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
- `openEO_2025-08-01Z`: a 10-daily NDVI composite product from Sentinel-2 L2A limited temporaly by `"2025-08-01" - "2025-08-10"` and limited spatially by the `aoi.json`
- `openEO_2025-08-11Z`: a 10-daily NDVI composite product from Sentinel-2 L2A limited temporaly by `"2025-08-11" - "2025-08-20"` and limited spatially by the `aoi.json`
- `openEO_2025-08-21Z`: a 10-daily NDVI composite product from Sentinel-2 L2A limited temporaly by `"2025-08-21" - "2025-08-31"` and limited spatially by the `aoi.json`


# The code in images
### Visualizing important parts of the code and proposing ideas
<img width="1920" height="1080" alt="Initial DataCube" src="https://github.com/user-attachments/assets/0e8daf7a-f08c-4dff-b7b9-f2b65ed40cc1" />
<img width="1920" height="1080" alt="Initial DataCube(2)" src="https://github.com/user-attachments/assets/1c3826ca-691a-4f52-a6f8-f276b904bcb3" />



### Part 2
Part 2 includes a conceptual workflow describing the steps to onboard data efficiently using the Sentinel Hub BYOC API. The link was created using [Canva](https://www.canva.com/)
You can find the workflow [here](https://www.canva.com/design/DAHApMHdwdk/8I58NmAHh-QdGZAbVoC_RQ/view?utm_content=DAHApMHdwdk&utm_campaign=designshare&utm_medium=link2&utm_source=uniquelinks&utlId=h0935883c7f).

# Further Improvements
- Use logger to save errors and warnings
- Add the Python `if __name__ == "__main__"` idiom to prevent execution at import time
- Handle NaN values at the edges
- Add more exceptions
- Further code improving and formatting
- Add sanity tests (visualize the data, print statistics)

