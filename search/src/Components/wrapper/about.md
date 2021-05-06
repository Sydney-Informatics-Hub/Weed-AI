# Welcome to Weed-AI.

### *Supporting the AI revolution in weed control*

Weeds, by definition, are plants in the wrong place but Weed-AI is helping put weed image data in the right place. Weed-AI is an open source, searchable, weeds image data platform designed to facilitate the research and development of machine learning algorithms for weed recognition in cropping systems.

# The need for AI in weed control

The default method of weed control in large-scale agriculture is field-wide treatments. Site-specific weed control (SSWC) is a more fine-grained approach where weed control treatments are applied only to targeted weeds. Under this approach, off-target land and crop are not exposed to the weed control method. Compared to field-wide herbicide treatments, the volume of herbicide applied to the land under SSWC is dramatically reduced. By performing targeted weed control, in-crop, SSWC also enables the use of novel, non-selective weed control technologies (such as lasers, microwaves and electrocution).

The success of SSWC depends on accurate detection and localisation of weeds, the combination termed weed recognition. While many powerful algorithms have been published for detection and recognition tasks, they have been trained on urban data. Unlike objects typical of urban scenes, crop and weeds display highly variable morphologies as they grow. There can be strong similarities between crop and weeds, particularly for closely related species. Adapting the state-of-the-art classification, detection and segmentation algorithms requires the availability of large quantities adequate training data. A major bottleneck in the development of effective weed recognition is annotating imagery, a typically slow and labour-intensive process. Weed-AI is addressing these challenges by enabling the easy access and contribution of annotated weed image data with standardised metadata on an open source platform with upload, search, dynamic filter and preview functions.

## How is Weed-AI different?

Currently publicly available weed datasets are fragmented and collected, stored and managed by multiple institutions. While the availability of this data is beneficial, this piecemeal approach lacks standards, structure, user-friendly search and the convenience of storing datasets together in one place. For example, a [review](https://www.sciencedirect.com/science/article/pii/S0168169920312709) of weed-specific datasets by Lu and Young 2020 found 15 were available at the time of writing each with varying degrees of metadata and all in different locations for download.

Weed-AI supports the contribution of users' own annotated weeds image data, browsing of existing data on the platform and download of whole datasets in a simple click.

# Navigating Weed-AI

### Explore

The [Explore](/explore) tab lets you filter and search all currently available datasets to find the image data that suit your purposes. Selecting an image will take you to the dataset summary page, providing detail on the dataset wide metadata including information such as camera specifications, crop stage and background conditions.

### Datasets

The datasets are listed on the [Datasets](/datasets) page. Select any dataset to read dataset wide metadata, to view image samples and to download the complete dataset.

To support the largest number of use cases, the unique demands of SSWC technology development and to ensure future utility of the system, we have developed a standard for representing annotated weeds image data, [WeedCOCO](/weedcoco).

### Upload

Contributing your own datasets to Weed-AI is streamlined on the [Upload](/upload) page. See that page to create a Weed-AI account or log in with your Google details to begin the upload process.

## WeedCOCO

WeedCOCO is our format for representing weed identification annotations.

# Citation Guidelines

## General

If you found Weed-AI useful in your research or project, please cite the database as:

_Weed-AI: A repository of Weed Images in Crops._ Precision Weed Control Group and Sydney Informatics Hub, the University of Sydney. https://weed-ai.sydney.edu.au/, accessed YYYY-MM-DD.

An academic  citation is TBA. 

## Specific Datasets

Each set of imagery used within the database should also be cited with the correct database Digital Object Identifier (DOI) and relevant papers.

# Acknowledgements
The development of Weed-AI has been funded by the [Grains Research and Development Corporation (GRDC)](https://grdc.com.au) PROC-9175960 grant. The platform was developed by the [Sydney Informatics Hub](https://www.sydney.edu.au/research/facilities/sydney-informatics-hub.html), a core research facility of the University of Sydney, as part of a research collaboration with the [Australian Centre for Field Robotics](https://www.sydney.edu.au/engineering/our-research/robotics-and-intelligent-systems/australian-centre-for-field-robotics.html) and the [Precision Weed Control Group](https://www.sydney.edu.au/science/our-research/research-areas/life-and-environmental-sciences/precision-weed-control-group.html) at the University of Sydney.

The software is open source and open to contribution on [GitHub](https://github.com/Sydney-Informatics-Hub/Weed-ID-Interchange). If you have any issues, suggestions or would like to contribute to the project please do so through Github or by emailing [weed-ai.app@sydney.edu.au](mailto:weed-ai.app@sydney.edu.au).

[![The University of Sydney logo](/usyd-logo.png "The University of Sydney")](https://sydney.edu.au)

We make use of [data from EPPO](https://data.eppo.int/) to validate and cross-reference plant species information, in accordance with the [EPPO Codes Open Data Licence](https://data.eppo.int/media/Open_Licence.pdf).

# Privacy

The collection of information is bound by our [Privacy Policy](/privacy).
