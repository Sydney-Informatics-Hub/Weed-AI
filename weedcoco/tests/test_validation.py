"""Tests for weedcoco.validation"""

import functools
import copy
import random

import pytest
import jsonschema

from weedcoco.validation import (
    validate,
    validate_json,
    validate_references,
    validate_coordinates,
    validate_image_sizes,
    ValidationError,
)

validate_image_sizes_null = functools.partial(validate_image_sizes, images_root=None)
validate_image_sizes_cwd = functools.partial(validate_image_sizes, images_root=".")


MINIMAL_WEEDCOCO = {
    "images": [],
    "annotations": [],
    "categories": [],
    "agcontexts": [],
    "collections": [],
    "collection_memberships": [],
    "info": {},
}

SMALL_WEEDCOCO = {
    "images": [
        {
            "id": 46,
            "file_name": "cwfid_images/046_image.png",
            "license": 0,
            "agcontext_id": 0,
            "width": 1296,
            "height": 966,
            "resolution": 1251936,
        },
        {
            "id": 1,
            "file_name": "cwfid_images/001_image.png",
            "license": 0,
            "agcontext_id": 0,
            "width": 1296,
            "height": 966,
            "resolution": 1251936,
        },
    ],
    "annotations": [
        {
            "id": 0,
            "image_id": 46,
            "category_id": 0,
            "segmentation": [[596, 207, 521, 153, 498, 89]],
            "iscrowd": 0,
        },
        {
            "id": 1,
            "image_id": 46,
            "category_id": 0,
            "segmentation": [
                [
                    689,
                    787,
                    589,
                    745,
                    553,
                    794,
                    553,
                    857,
                    573,
                    886,
                    642,
                    886,
                    678,
                    850,
                    707,
                    814,
                ]
            ],
            "iscrowd": 0,
        },
        {
            "id": 2,
            "image_id": 46,
            "category_id": 1,
            "segmentation": [[486, 335, 399, 395, 354, 490]],
            "iscrowd": 0,
        },
        {
            "id": 3,
            "image_id": 1,
            "category_id": 1,
            "segmentation": [[810, 225, 841, 234, 846, 266]],
            "iscrowd": 0,
        },
        {
            "id": 4,
            "image_id": 1,
            "category_id": 1,
            "segmentation": [[1070, 626, 1055, 722, 980, 739]],
            "iscrowd": 0,
        },
    ],
    "categories": [
        {
            "name": "crop: daugus carota",
            "common_name": "carrot",
            "species": "daugus carota",
            "eppo_taxon_code": "DAUCS",
            "eppo_nontaxon_code": "3UMRC",
            "role": "crop",
            "id": 0,
        },
        {
            "name": "weed: unspecified",
            "species": "UNSPECIFIED",
            "role": "weed",
            "id": 1,
        },
    ],
    "info": {
        "version": 1,
        "description": "Cwfid annotations converted into WeedCOCO",
        "id": 0,
    },
    "license": [
        {
            "id": 0,
            "license_name": "CC BY 4.0",
            "license_fullname": "Creative Commons Attribution 4.0",
            "license_version": "4.0",
            "url": "https://creativecommons.org/licenses/by/4.0/",
        }
    ],
    "agcontexts": [
        {
            "id": 0,
            "agcontext_name": "cwfid",
            "crop_type": "other",
            "bbch_descriptive_text": "leaf development",
            "bbch_code": "gs10",
            "grains_descriptive_text": "seedling",
            "soil_colour": "grey",
            "surface_cover": "none",
            "surface_coverage": "0-25",
            "weather_description": "sunny",
            "location_lat": 53,
            "location_long": 11,
            "location_datum": 4326,
            "camera_make": "JAI AD-130GE",
            "camera_lens": "Fujinon TF15-DA-8",
            "camera_lens_focallength": 15,
            "camera_height": 450,
            "camera_angle": 90,
            "camera_fov": 22.6,
            "photography_description": "Mounted on boom",
            "lighting": "natural",
            "cropped_to_plant": False,
        }
    ],
    "collections": [
        {
            "author": "Haug, Sebastian and Ostermann, J\u00f6rn",
            "title": "A Crop/Weed Field Image Dataset for the Evaluation of Computer Vision Based Precision Agriculture Tasks",
            "year": 2015,
            "identifier": "doi:10.1007/978-3-319-16220-1_8",
            "rights": "All data is subject to copyright and may only be used for non-commercial research. In case of use please cite our publication.",
            "accrual_policy": "closed",
            "url": "https://github.com/cwfid/dataset",
            "id": 0,
        }
    ],
    "collection_memberships": [
        {"annotation_id": 0, "subset": "train", "collection_id": 0},
        {"annotation_id": 1, "subset": "train", "collection_id": 0},
        {"annotation_id": 2, "subset": "train", "collection_id": 0},
        {"annotation_id": 3, "subset": "train", "collection_id": 0},
        {"annotation_id": 4, "subset": "train", "collection_id": 0},
    ],
}


@pytest.mark.parametrize("func", [validate, validate_json])
@pytest.mark.parametrize(
    "bad_weedcoco",
    [
        {},
        {"images": [], "annotations": []},
        {"images": [], "annotations": [], "categories": []},
    ],
)
def test_missing_required_at_root(func, bad_weedcoco):
    with pytest.raises(jsonschema.ValidationError, match="is a required property"):
        func(bad_weedcoco)


@pytest.mark.parametrize(
    "func",
    [
        validate,
        validate_json,
        validate_references,
        validate_coordinates,
        validate_image_sizes_null,
        validate_image_sizes_cwd,
    ],
)
def test_okay(func):
    func(MINIMAL_WEEDCOCO)
    func(SMALL_WEEDCOCO)


"""
@pytest.mark.parametrize("func", [validate, validate_json])
@pytest.mark.parametrize("bad_name", [])
def test_bad_category_name(func, bad_name):
    weedcoco = copy.deepcopy(SMALL_WEEDCOCO)
    weedcoco["categories"][0]["name"] == name
"""


def _make_duplicate_id(weedcoco, key, idx, insert_at=-1):
    weedcoco = copy.deepcopy(weedcoco)
    weedcoco[key].insert(insert_at, weedcoco[key][idx])
    return weedcoco


@pytest.mark.parametrize("func", [validate, validate_json])
@pytest.mark.parametrize(
    "removed_section",
    [
        "images",
        "annotations",
        "categories",
        "collections",
        "collection_memberships",
        "agcontexts",
    ],
)
def test_missing_section(func, removed_section):
    bad_weedcoco = copy.deepcopy(SMALL_WEEDCOCO)
    del bad_weedcoco[removed_section]
    with pytest.raises(jsonschema.ValidationError):
        func(bad_weedcoco)


@pytest.mark.parametrize("func", [validate, validate_references])
@pytest.mark.parametrize(
    "bad_weedcoco",
    [
        _make_duplicate_id(SMALL_WEEDCOCO, "images", idx=0),
        _make_duplicate_id(SMALL_WEEDCOCO, "images", idx=0, insert_at=0),
        _make_duplicate_id(SMALL_WEEDCOCO, "annotations", idx=2, insert_at=4),
        _make_duplicate_id(SMALL_WEEDCOCO, "collections", idx=0),
    ],
)  # TODO
def test_duplicate_id(func, bad_weedcoco):
    with pytest.raises(ValidationError, match="Duplicate ID"):
        func(bad_weedcoco)


def _make_unknown_id(weedcoco, section, ref_key, new_id=1000):
    bad_weedcoco = copy.deepcopy(weedcoco)
    random.choice(bad_weedcoco[section])[ref_key] = new_id
    return bad_weedcoco


@pytest.mark.parametrize("func", [validate, validate_references])
@pytest.mark.parametrize(
    "bad_weedcoco",
    [
        _make_unknown_id(SMALL_WEEDCOCO, "annotations", "image_id"),
        _make_unknown_id(SMALL_WEEDCOCO, "annotations", "category_id"),
        _make_unknown_id(SMALL_WEEDCOCO, "collection_memberships", "collection_id"),
        _make_unknown_id(SMALL_WEEDCOCO, "collection_memberships", "annotation_id"),
    ],
)  # TODO
def test_nonexistent_referent(func, bad_weedcoco):
    with pytest.raises(ValidationError, match="Reference to unknown ID"):
        func(bad_weedcoco)


def _make_unreferenced(weedcoco, section, new_id=1000):
    bad_weedcoco = copy.deepcopy(weedcoco)
    copied = copy.deepcopy(random.choice(bad_weedcoco[section]))
    copied["id"] = new_id
    bad_weedcoco[section].insert(random.randint(0, len(bad_weedcoco[section])), copied)
    return bad_weedcoco


@pytest.mark.parametrize("func", [validate, validate_references])
@pytest.mark.parametrize(
    "bad_weedcoco",
    [
        _make_unreferenced(SMALL_WEEDCOCO, "collections"),
        _make_unreferenced(SMALL_WEEDCOCO, "images"),
    ],
)  # TODO
def test_id_not_referenced(func, bad_weedcoco):
    with pytest.raises(ValidationError, match="is unreferenced"):
        func(bad_weedcoco)


# TODO: Test invalid bbox coordinates and boundary cases
# TODO: Test invalid polygon coordinates
