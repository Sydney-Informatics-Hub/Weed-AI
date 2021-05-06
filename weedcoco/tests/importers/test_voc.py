import pathlib
import json

import pytest

from weedcoco.importers.voc import main

TEST_DATA_DIR = pathlib.Path(__file__).parent / "voc_data"
TEST_VOC_DIR = TEST_DATA_DIR / "VOC"
TEST_IMAGE_DIR = TEST_DATA_DIR / "images"
AGCONTEXT = {
    "bbch_growth_range": "na",
    "camera_angle": 12,
    "camera_fov": "variable",
    "camera_height": 666,
    "camera_lens": "dunno",
    "camera_lens_focallength": 555,
    "camera_make": "dunno",
    "crop_type": "wheat",
    "cropped_to_plant": False,
    "id": 0,
    "ground_speed": 0,
    "lighting": "artificial",
    "location_lat": 90,
    "location_long": 90,
    "photography_description": "foobar",
    "soil_colour": "grey",
    "surface_cover": "none",
    "surface_coverage": "0-25",
    "weather_description": "Nothing to note",
}
ANNOTATIONS_WITH_RYEGRASS_0 = [
    {"bbox": [146, 747, 27, 45], "category_id": 0, "id": 0, "image_id": 0},
    {"bbox": [817, 835, 42, 55], "category_id": 0, "id": 1, "image_id": 1},
    {"bbox": [1163, 314, 28, 16], "category_id": 1, "id": 2, "image_id": 1},
    {"bbox": [1511, 208, 21, 31], "category_id": 1, "id": 3, "image_id": 1},
]
COMPLETE_WEEDCOCO = {
    "agcontexts": [AGCONTEXT],
    "annotations": ANNOTATIONS_WITH_RYEGRASS_0,
    "categories": [
        {"id": 0, "name": "weed: lolium perenne"},
        {"id": 1, "name": "weed: rapistrum rugosum"},
    ],
    "images": [
        {
            "agcontext_id": 0,
            "file_name": "resizeC1_PLOT_20190728_175852.jpg",
            "height": 960,
            "id": 0,
            "width": 1536,
            "license": 0,
        },
        {
            "agcontext_id": 0,
            "file_name": "resizeC1_PLOT_20190728_180135.jpg",
            "height": 960,
            "id": 1,
            "width": 1536,
            "license": 0,
        },
    ],
    "licenses": [{"id": 0, "url": "https://creativecommons.org/licenses/by/4.0/"}],
    "info": {
        "description": "Dataset collected at Narrabri under artificial illumination",
        "year": 2020,
        "metadata": {
            "name": "Dataset collected at Narrabri under artificial illumination",
            "description": "Dataset collected at Narrabri under artificial illumination",
            "creator": [{"name": "Plony", "@type": "Person"}],
            "datePublished": "2020-XX-XX",
            "license": "https://creativecommons.org/licenses/by/4.0/",
        },
    },
}


@pytest.fixture
def converter(tmpdir):
    out_path = tmpdir / "out.json"

    class Converter:
        def run(self, extra_args, voc_dir=TEST_VOC_DIR, image_dir=TEST_IMAGE_DIR):
            args = ["--voc-dir", voc_dir, "--image-dir", image_dir, "-o", out_path]
            args.extend(extra_args)
            args = [str(arg) for arg in args]
            main(args)
            return json.load(out_path)

    return Converter()


def test_no_data(converter):
    with pytest.raises(SystemExit):
        converter.run([], voc_dir=TEST_IMAGE_DIR)


def test_no_extras(converter):
    expected = {
        "annotations": ANNOTATIONS_WITH_RYEGRASS_0,
        "categories": [{"id": 0, "name": "Ryegrass"}, {"id": 1, "name": "Turnip"}],
        "images": [
            {
                "file_name": "resizeC1_PLOT_20190728_175852.jpg",
                "height": 960,
                "id": 0,
                "width": 1536,
            },
            {
                "file_name": "resizeC1_PLOT_20190728_180135.jpg",
                "height": 960,
                "id": 1,
                "width": 1536,
            },
        ],
        "info": {},
    }
    assert expected == converter.run([])


def test_complete(converter):
    assert COMPLETE_WEEDCOCO == converter.run(
        [
            "--agcontext-path",
            TEST_DATA_DIR / "agcontext.yaml",
            "--metadata-path",
            TEST_DATA_DIR / "metadata1.json",
            "--category-name-map",
            TEST_DATA_DIR / "category_name_map1.yaml",
            "--validate",
        ]
    )


def test_category_name_map2(converter):
    result = converter.run(
        [
            "--agcontext-path",
            TEST_DATA_DIR / "agcontext.yaml",
            "--metadata-path",
            TEST_DATA_DIR / "metadata1.json",
            "--category-name-map",
            TEST_DATA_DIR / "category_name_map2.yaml",
            "--validate",
        ]
    )

    def _get_name_for_annotation(coco, ann):
        for cat in coco["categories"]:
            if cat["id"] == ann["category_id"]:
                return cat["name"]
        assert False

    # category_name_map2 has categories in a different order to category_name_map1.
    assert result["categories"] == [
        {"id": 0, "name": "weed: raphanus raphanistrum"},
        {"id": 1, "name": "weed: rapistrum rugosum"},
        {"id": 2, "name": "weed: lolium perenne"},
    ]
    # check category names match up with category_name_map1.yaml
    for i, annotation in enumerate(result["annotations"]):
        assert _get_name_for_annotation(result, annotation) == _get_name_for_annotation(
            COMPLETE_WEEDCOCO, COMPLETE_WEEDCOCO["annotations"][i]
        )
