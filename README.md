[![DOI](https://zenodo.org/badge/627146632.svg)](https://zenodo.org/badge/latestdoi/627146632)

# Remotely Sensed Crop Stress Early Indicator

Can satellite remote sensing detect early stage crop stress at high resolution across whole-farm scale?

Hydrosat produces a proprietary "fused" thermal infrared land surface temperature (LST) imagery product using sharpening and interpolation algorithms to produce near daily sub-30 m resolution imagery from a combination of MODIS, Sentinel and Landsat imaging platforms. This project aims to explore the input data and intermediate outputs of the algorithms used to produce the LST product in order to detect errors potentially introduced by data quality issues or the application of the algorithms while also exploring applications within agricultural contexts.

See the blog post [here](https://tcruicks.github.io/blog.html).

Github Repository: [here](https://github.com/tcruicks/tcruicks-capstone-catd/tree/master)

# Collaborators and Acknowledgements

- [Erik Anderson](https://github.com/eriktuck)
- [Tyler Cruickshank](https://github.com/tcruicks)
- [Joe McGlinchy](https://github.com/joemcglinchy)

We thank Joe McGlinchy of Hydrosat for providing project guidance and data access.

# Directory structure and explanation

* `library/`: This directory stores modularized code for use in the notebook. This allows the library module to be imported directly (as opposed to a "src layout that would need to be installed).
* `exploratory/`: A place for the main project Jupyter notebook and .py script modules.
* `assets/`: stores images and gifs used in the final blog
* `secrets/`: store individuals credentials here, so that anyone can run anyone else's code, provided they have input their own credentials in the correct format.
* `data/`: holds ameriflux met data and hrrr model data which can be used instead of observed met data.
* `blog/`: holds project blog.html file and images.  Also holds the project notebook titled blog.ipynb.

# Environment
To reproduce this workflow, use the provided `tcruicks-final-catd.yml` file to create a `conda` environment (you should already have Python and `conda` installed on your system).

After cloning this directory to your system, use the following `bash` commands to create and activate the environment:

```bash
conda env create -f tcruicks-final-catd.yml
conda activate ea-lst-alpha
```

You must have Jupyter Notebook installed on your system to run this analysis. For installation instructions, consult the documentation [here](https://jupyter.org/).

Once Jupyter Notebook is installed, install the iPython kernel in the environment. With the environment activated, in bash use the command:

```bash
ipython kernel install --name ea-lst-alpha --user
```

The `--name` flag specifies the name the kernel will appear under when selecting it to use with Jupyter Notebooks. It's best to name it the same as the environment name.

# Data

For access to Hydrosat's proprietary products, you must receive credentials using the instructions described at the [Hydrosat Fusion Hub](https://hydrosat.github.io/fusion-hub-docs/intro.html). Add your credentials to the `secrets/` folder in a file called `creds.json` with the format:

```json
{
    "username":"",
    "password":""
}
```
See the [Hydrosat Fusion Hub Documentation](https://hydrosat.github.io/fusion-hub-docs/intro.html) for additional guidance.

Meteorological data are provided by [Ameriflux](https://ameriflux.lbl.gov/) and included in the project's `data/Ameriflux` directory.

## Setup the analysis
To reproduce the analysis in [here](https://tcruicks.github.io/blog.html), first follow the instructions to set up the environment and access data, described above. 

Open the file [Here](https://github.com/tcruicks/tcruicks-capstone-catd/blob/master/exploratory/tcruicks-final-catd.ipynb) in a Jupyter Notebook.

1) Cell #3: Create a creds.json file with your STAC id and password.  Place the file in /secrets/creds.json.
2) Cell #4: Analysis name (& number), crop field center points, met tower locations, crop field area of interest box coordinates (AOI), coordinates for point extractions. * To create and get AOI coords, use Google Earth to draw a polygon.  Export the polygon as a KML file.  Open KML file and grab the coordinates.
3) Now you can run the analysis.  Note that some code cells may take up to an hour to run.
  
Note that Hydrosat does not currently include coverage for the entire CONUS area and so confirm the coverage of data for any new meteorological tower location.

## Visuals created by code

1. Folium map of study locations
2. Plot of Sentinel 2 mean NDVI and variance
3. Plot of Sentinel 2 mean NDVI only.
4. Boxplot of all Sentinel 2 AOI NDVI values.
5. Plots of CATD for all fusion assets.
6. Plot of CATD for fusion CATD only.
7. Boxplots for AOI CATD values for all fusion assets.
8. Plot of time-series mean fusion CATD and NDVI.
9. Plot of time-series single pixel fusion CATD and NDVI.
10. Optional plots of air temperature, wind speed, and relative humidity

## Convert to HTML report
To convert the file `blog.ipynb` to an HTML report, you must have the library `nbconvert` installed (note that this library is not included in this project's environment; read the [documentation](https://nbconvert.readthedocs.io/en/latest/) for installation instructions). 

Use the following bash command to convert the notebook and post to gh-pages:

```bash
jupyter nbconvert --to html_embed --no-input blog.ipynb
mv blog.html index.html
git commit -am "update blog"
git pull
git push origin main
git checkout gh-pages
git checkout main index.html
git commit -am "updating gh-pages"
git push origin gh-pages
git checkout main
```

## Issues 
The processing of the imagery is extremely computationally intensive.  Some code cells require one hour to execute.  Internet traffic can interrupt processing as well. 

## Needed Improvements
The notebook needs to be re-organized to seperate the processing of dataarrays from the actual analaysis because of computational intensive nature.  The current notebook makes use of loops to process all of the image assets.  In some ways. this makes the code more complicated because of the different specs of each image asset and the size of the AOI being use.

## How to Cite
cff-version: 1.2.0
message: "If you use this software, please cite it as below."
authors:
- family-names: "Cruickshank"
  given-names: "Tyler"
- family-names: "Erik"
  given-names: "Anderson"
- family-names: "Joeseph"
  given-names: "McGlinchy"
title: ">Early Detection of Crop Stress From Thermal Infrared Imagery"
version: 1.0
date-released: 2023-09-01
url: "https://github.com/tcruicks/tcruicks-capstone-catd/tree/master"
