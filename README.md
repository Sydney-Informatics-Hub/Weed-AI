# Welcome to Weed-AI

Weed-AI provides is an open source, searchable, weeds image platform designed to facilitate the research and development of machine learning algorithms for weed recognition in cropping systems.
It brings together existing datasets, enables users to contribute their own data and pulls together custom datasets for straightforward download. 

See our Weed Explorer at https://weed-ai.sydney.edu.au

# Background 

Large numbers of high quality, annotated weed images are essential for the development of weed recognition algorithms that are accurate and reliable in complex biological systems.
Accurate weed recognition enables the use of site-specific weed control (SSWC) in agricultural systems, eliminating the need for wasteful whole field treatments.
This approach substantially reduces weed control inputs and creates opportunities for the introduction of alternative weed control technologies that were not previously feasible for use as indiscriminate whole field treatments.
SSWC relies on accurate detection (is a weed present) and identification (what is the species/further information on morphology) of weeds in agricultural and environmental systems (crop, pastures, rangelands and non-crop areas, etc.).
Camera-based weed recognition using deep learning algorithms has emerged as a frontrunner for in-crop site-specific control with an improved ability to handle variation.

Training and development of algorithms require significant quantities of high-quality, annotated images.
Weed-AI is addressing this challenge by enabling the easy access and contribution of weed image data on an open source platform with search, dynamic filter and preview functions for custom dataset download capability. 

# Data supported 

To support the largest number of use cases and the unique demands of SSWC technology development, we have developed a standard for storing weed images and their anotations. 
Our standard - WeedCOCO - is an extension on Microsoft's Common Objects in Context format (MS COCO). 
WeedCOCO incorporates additional whole-dataset contextual information that provides descriptions of the agricultural context as well as details of how the images were capture.
This "AgContext" includes:

- Crop type 

- Crop growth stage (text and BBCH) 

- Soil colour 

- Surface coverage 

- Weather description 

- Location 

- Camera metadata (camera model, collection height, angle, lens, focal length, field of view) 

- Lighting  

The format may also be applicable to related agricultural purposes.
As with MS COCO, the format supports classification, bounding box and segmentation labels indicating the presence of a specific or unknown species of weed.
Reporting these details will help ensure consistency in published datasets for ease of comparison and use in further research and development.


![Weed-AI Data Flow](https://github.com/Sydney-Informatics-Hub/Weed-ID-Interchange/blob/master/weedID-data-flow-diagram.png)

# Acknowledgements 

This project has been funded by the Grains Research and Development Corporation.
The platform was developed by the Sydney Informatics Hub, a core research facility of the University of Sydney, as part of a research collaboration with the Australian Centre for Field Robotics and the Precision Weed Control Group at the University of Sydney.

We make use of [data from EPPO](https://data.eppo.int/) to validate and cross-reference plant species information, in accordance with the [EPPO Codes Open Data Licence](https://data.eppo.int/media/Open_Licence.pdf).

# Citation Guidelines 

## General 

If you found Weed-AI useful in your research, please cite the database as: 

CITATION TBA by mid 2021

## Specific Datasets 

Each set of imagery used within the database should also be cited with the correct database Digital Object Identifier (DOI) and relevant papers. 
