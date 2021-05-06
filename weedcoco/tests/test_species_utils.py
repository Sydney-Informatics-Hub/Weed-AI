import pytest
import tempfile
import pathlib

from weedcoco.species_utils import get_eppo_singleton

# Keep a cache of downloaded content across test runs
CACHE_DIR = pathlib.Path(tempfile.gettempdir()) / "weedcoco-test_species_util"


@pytest.fixture()
def eppo():
    CACHE_DIR.mkdir(exist_ok=True)
    return get_eppo_singleton(path=CACHE_DIR / "eppo_full_cache.zip", cache=True)


@pytest.mark.parametrize(
    "name,species_only,code",
    [
        ("lolium rigidum", False, "LOLRI"),
        ("lolium rigidum", True, "LOLRI"),
        ("Lolium rigidum", True, "LOLRI"),
        ("lolium", False, "1LOLG"),
    ],
)
def test_lookup_preferred_name(name, species_only, code, eppo):
    entry = eppo.lookup_preferred_name(name, species_only=species_only)
    assert entry["code"] == code


@pytest.mark.parametrize(
    "name,species_only,match",
    [
        ("lolium", True, "'lolium' is not a species"),
        ("lollium", False, "'lollium'"),
        ("Lollium", False, "'lollium'"),
        ("umbelliferae", True, "'umbelliferae'"),  # test handling of ispreferred
    ],
)
def test_lookup_preferred_name_error(name, species_only, match, eppo):
    with pytest.raises(KeyError, match=match):
        eppo.lookup_preferred_name(name, species_only=species_only)


@pytest.mark.parametrize(
    "name,species_only,code",
    [
        ("annual rye-grass", True, "LOLRI"),
        ("Annual Rye-grass", True, "LOLRI"),
        ("stiff darnel", True, "LOLRI"),
        ("wymmera ryegrass", True, "LOLRI"),
        ("carrot", False, "DAUCS"),  # test handling of isactive
        ("grasses", False, "1GRAF"),
    ],
)
def test_lookup_unique_name(name, species_only, code, eppo):
    entry = eppo.lookup_unique_name("en", name, species_only=species_only)
    assert entry["code"] == code


@pytest.mark.parametrize(
    "name,species_only,match",
    [
        ("grasses", True, "'grasses' is not a species"),
        ("ivraie rigide", False, "'ivraie rigide'"),
        # TODO: find non-unique name...
    ],
)
def test_lookup_unique_name_error(name, species_only, match, eppo):
    with pytest.raises(KeyError, match=match):
        eppo.lookup_unique_name("en", name, species_only=species_only)


@pytest.mark.parametrize(
    "name,species_only,codes",
    [
        ("annual rye-grass", True, {"LOLRI"}),
        ("Annual Rye-grass", True, {"LOLRI"}),
        ("grasses", False, {"1GRAF"}),
        # TODO: find non-unique name...
    ],
)
def test_lookup_name(name, species_only, codes, eppo):
    entries = eppo.lookup_name("en", name, species_only=species_only)
    assert sorted(codes) == sorted(entry["code"] for entry in entries)


def test_entries(eppo):
    entry = eppo.entries["1GRAF"]
    assert entry["code"] == "1GRAF"
    assert entry["level"] == "group"
    assert entry["preferred_name"] == "Poaceae"
    assert "grasses" in entry["en_names"]
    assert "1POOS" in entry["children"]
    assert "1BAMS" in entry["children"]
    assert entry["parent_code"] == "1POAO"
    assert entry["ancestors"] == ["1POAO", "1COMD", "1ANGC", "1MAGP", "1PLAK"]
    assert entry.keys() == {
        "code",
        "level",
        "preferred_name",
        "en_names",
        "children",
        "parent_code",
        "ancestors",
    }

    childless_entry = eppo.entries["LOLRI"]
    assert childless_entry.keys() == {
        "code",
        "level",
        "preferred_name",
        "en_names",
        "parent_code",
        "ancestors",
    }


# TODO: test alternative langs/types
