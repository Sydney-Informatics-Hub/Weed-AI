import pathlib
import pytest

from elasticmock import elasticmock as elasticmock
from weedcoco.index.indexing import main, ElasticSearchIndexer

BASIC_INPUT_PATH = str(
    pathlib.Path(__file__).parent.parent
    / "repo"
    / "deposit_data"
    / "basic_1"
    / "weedcoco.json"
)
THUMBNAIL_DIR = "arbitrary-thumbnail-dir"


@elasticmock
def test_smoke_indexing():
    # run indexing but check nothing
    main(["--weedcoco-path", BASIC_INPUT_PATH, "--thumbnail-dir", THUMBNAIL_DIR])


def test_batch_generation():
    # TODO
    pytest.xfail("Not yet implemented")


def test_task_type():
    indexer = ElasticSearchIndexer(
        weedcoco_path=BASIC_INPUT_PATH, thumbnail_dir=THUMBNAIL_DIR
    )
    for entry in indexer.generate_index_entries():
        assert isinstance(entry["task_type"], list)
    # TODO: test the task type for different input annotation data
    # TODO: test for "segmentation": []
    pytest.xfail("Not yet implemented")


def test_annotation_and_category():
    "Check annotations and categories are correctly indexed with each image"
    indexer = ElasticSearchIndexer(
        weedcoco_path=BASIC_INPUT_PATH, thumbnail_dir=THUMBNAIL_DIR
    )
    expected_names = {
        0: {"name": "crop: daucus carota", "taxo_names": {"crop: daucus carota"}},
        1: {"name": "weed: UNSPECIFIED", "taxo_names": {"weed: UNSPECIFIED", "weed"}},
        2: {
            "name": "weed: sonchus oleraceus",
            "taxo_names": {
                "weed: sonchus oleraceus",
                "weed: non-poaceae",
                "weed: asteraceae",
                "weed",
            },
        },
        3: {
            "name": "weed: lolium perenne",
            "taxo_names": {"weed: lolium perenne", "weed: poaceae", "weed"},
        },
    }
    for entry in indexer.generate_index_entries():
        assert entry["annotations"]  # TODO: check correct number of annotations
        for annotation in entry["annotations"]:
            category_id = annotation["category_id"]
            assert annotation["category"]["name"] == expected_names[category_id]["name"]
            assert (
                set(annotation["category"]["taxo_names"])
                == expected_names[category_id]["taxo_names"]
            )


def test_growth_range():
    indexer = ElasticSearchIndexer(
        weedcoco_path=BASIC_INPUT_PATH, thumbnail_dir=THUMBNAIL_DIR
    )
    for entry in indexer.generate_index_entries():
        growth_range = entry["agcontext"]["bbch_growth_range"]
        assert growth_range == {"min": 10, "max": 20}
        growth_stage_texts = entry["agcontext"]["growth_stage_texts"]
        assert len(growth_stage_texts) == 2
        assert entry["agcontext"]["growth_stage_min_text"] in growth_stage_texts
        assert entry["agcontext"]["growth_stage_max_text"] in growth_stage_texts
        assert (
            entry["agcontext"]["growth_stage_max_text"]
            != entry["agcontext"]["growth_stage_min_text"]
        )
