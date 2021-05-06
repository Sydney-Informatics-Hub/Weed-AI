"""Tests for weedcoco.validation"""

import functools
import copy
import random
import re

import pytest

from weedcoco.validation import (
    validate,
    validate_json,
    validate_references,
    validate_coordinates,
    validate_image_sizes,
    ValidationError,
    JsonValidationError,
)
from .testcases import (
    MINIMAL_WEEDCOCO,
    SMALL_WEEDCOCO,
    test_missing_required_at_root_expected,
)

validate_image_sizes_null = functools.partial(validate_image_sizes, images_root=None)
validate_image_sizes_cwd = functools.partial(validate_image_sizes, images_root=".")


def _set_category_name(coco, name):
    coco = copy.deepcopy(coco)
    coco["categories"][0]["name"] = name
    return coco


def _remove_schema_from_error(error):
    for error_detail in error["error_details"]:
        error_detail.pop("schema", None)
    return error


@pytest.mark.parametrize(
    "func,bad_weedcoco,expected",
    zip(
        [validate_json] * 3,
        [
            {},
            {"images": [], "annotations": []},
            {"images": [], "annotations": [], "categories": []},
        ],
        test_missing_required_at_root_expected,
    ),
)
def test_missing_required_at_root(func, bad_weedcoco, expected):
    with pytest.raises(JsonValidationError, match="is a required property") as e:
        func(bad_weedcoco)
    assert _remove_schema_from_error(e.value.get_error_details()) == expected


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


@pytest.mark.parametrize("func", [validate, validate_json])
@pytest.mark.parametrize(
    "bad_name,messages",
    [
        ("foobar", ["is not a 'weedcoco_category'", "does not match"]),
        ("weed 1", ["is not a 'weedcoco_category'", "does not match"]),
        ("crop: UNSPECIFIED", ["is not a 'weedcoco_category'"]),
        ("crop: daugus carotta", ["is not a 'weedcoco_category'"]),
        ("weed: lollium rigidum", ["is not a 'weedcoco_category'"]),
        ("weed: Triticum Aestivum", ["is not a 'weedcoco_category'", "does not match"]),
    ],
)
def test_bad_category_name(func, bad_name, messages):
    weedcoco = copy.deepcopy(SMALL_WEEDCOCO)
    weedcoco = _set_category_name(weedcoco, bad_name)
    with pytest.raises(JsonValidationError, match=repr(bad_name)) as e:
        func(weedcoco)
    expected = {
        "error_type": "jsonschema",
        "n_errors_found": str(len(messages)),
    }
    actual_errors = _remove_schema_from_error(e.value.get_error_details())
    actual_details = actual_errors.pop("error_details")
    assert expected == actual_errors
    assert all(d["path"] == ["categories", 0, "name"] for d in actual_details)
    assert all(d["value"] == bad_name for d in actual_details)
    assert all(
        re.match(f"{re.escape(repr(bad_name))} {message}", d["message"])
        for d, message in zip(actual_details, messages)
    )


@pytest.mark.parametrize("func", [validate, validate_json])
@pytest.mark.parametrize(
    "bad_name",
    [
        "wheat",
        "oats",
        "pasture",
        "fallow",
        "daucus carota",
        "brassica oleracea var. alboglabra",
    ],
)
def test_crop_type(func, bad_name):
    weedcoco = copy.deepcopy(SMALL_WEEDCOCO)
    weedcoco["agcontexts"][0]["crop_type"] = bad_name
    func(weedcoco)


@pytest.mark.parametrize("func", [validate, validate_json])
@pytest.mark.parametrize(
    "bad_name",
    [
        "weet",
        "daugus carota",
    ],
)
def test_bad_crop_type(func, bad_name):
    weedcoco = copy.deepcopy(SMALL_WEEDCOCO)
    weedcoco["agcontexts"][0]["crop_type"] = bad_name
    with pytest.raises(ValidationError):
        func(weedcoco)


@pytest.mark.parametrize("func", [validate_json])
@pytest.mark.parametrize(
    "name",
    [
        "weed",
        "crop",
        "none",
        "weed: UNSPECIFIED",
        "crop: triticum aestivum",
        "weed: triticum aestivum",
    ],
)
def test_category_name(func, name):
    weedcoco = copy.deepcopy(SMALL_WEEDCOCO)
    weedcoco = _set_category_name(weedcoco, name)
    func(weedcoco)


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
        "agcontexts",
    ],
)
def test_missing_section(func, removed_section):
    bad_weedcoco = copy.deepcopy(SMALL_WEEDCOCO)
    del bad_weedcoco[removed_section]
    with pytest.raises(JsonValidationError):
        func(bad_weedcoco)


@pytest.mark.parametrize("func", [validate, validate_references])
@pytest.mark.parametrize(
    "bad_weedcoco",
    [
        _make_duplicate_id(SMALL_WEEDCOCO, "images", idx=0),
        _make_duplicate_id(SMALL_WEEDCOCO, "images", idx=0, insert_at=0),
        _make_duplicate_id(SMALL_WEEDCOCO, "annotations", idx=2, insert_at=4),
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
        _make_unreferenced(SMALL_WEEDCOCO, "images"),
    ],
)  # TODO
def test_id_not_referenced(func, bad_weedcoco):
    with pytest.raises(ValidationError, match="is unreferenced"):
        func(bad_weedcoco)


def _weedcoco_to_coco(weedcoco):
    coco = copy.deepcopy(weedcoco)
    del coco["agcontexts"]
    del coco["info"]["metadata"]
    for image in coco["images"]:
        del image["agcontext_id"]
    return coco


@pytest.mark.parametrize("func", [validate, validate_json])
@pytest.mark.parametrize(
    "coco",
    [
        _weedcoco_to_coco(MINIMAL_WEEDCOCO),
        _weedcoco_to_coco(SMALL_WEEDCOCO),
    ],
)
def test_coco_compatible_good(func, coco):
    func(coco, schema="compatible-coco")


@pytest.mark.parametrize("func", [validate, validate_json])
@pytest.mark.parametrize(
    "bad_coco",
    [
        # drop categories:
        {
            k: v
            for k, v in _weedcoco_to_coco(MINIMAL_WEEDCOCO).items()
            if k != "categories"
        },
        # drop annotations:
        {
            k: v
            for k, v in _weedcoco_to_coco(MINIMAL_WEEDCOCO).items()
            if k != "annotations"
        },
        # rename to WeedCOCO-incompatible categories:
        _set_category_name(_weedcoco_to_coco(SMALL_WEEDCOCO), "foobar"),
    ],
)
def test_coco_compatible_bad(func, bad_coco):
    with pytest.raises(JsonValidationError):
        func(bad_coco, schema="compatible-coco")
