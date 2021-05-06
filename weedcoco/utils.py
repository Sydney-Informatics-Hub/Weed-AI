import json
import pathlib
import os
import warnings

import PIL.Image
import yaml
import imagehash

from .species_utils import get_eppo_singleton

EPPO_PATH = "_eppo_xmlfull.zip"


def set_info(coco, metadata):
    info = coco.get("info", {}).copy()
    info["metadata"] = metadata
    info["description"] = metadata["name"]
    try:
        info["year"] = int(metadata["datePublished"][:4])
    except Exception:
        pass
    coco["info"] = info


def set_licenses(coco, metadata=None):
    """Set the license for each image to be that from the metadata"""
    if metadata is None:
        metadata = coco["info"]["metadata"]
    coco["licenses"] = [{"id": 0, "url": metadata["license"]}]
    for image in coco["images"]:
        image["license"] = 0


def get_image_dimensions(path):
    """
    Function to measure image dimensions and calculate resolution.
    """
    if not os.path.isfile(path):
        warnings.warn(f"Could not open {path}")
        return None
    # Retrieve image width and height
    image = PIL.Image.open(path)
    width, height = image.size
    return {"width": width, "height": height}


def load_json_or_yaml(path):
    """Streamlined function for open both JSON and YAML"""
    with open(path) as f:
        if path.suffix in (".yml", ".yaml"):
            obj = yaml.safe_load(f)
        else:
            obj = json.load(f)
    return obj


def add_agcontext_from_file(coco, agcontext_path):
    """Make all images have the same AgContext loaded from YAML or JSON"""
    agcontext = load_json_or_yaml(agcontext_path)
    if "id" not in agcontext:
        agcontext["id"] = 0
    coco["agcontexts"] = [agcontext]
    for image in coco["images"]:
        image["agcontext_id"] = agcontext["id"]
    return coco


def add_metadata_from_file(coco, metadata_path):
    """Load metadata from YAML or JSON to set info and licenses"""
    metadata = load_json_or_yaml(metadata_path)
    set_info(coco, metadata)
    set_licenses(coco)
    return coco


def get_image_average_hash(path, hash_size=8):
    """Return an average hash of an image"""
    return str(imagehash.average_hash(PIL.Image.open(path), hash_size=hash_size))


def check_if_approved_image_extension(image_name):
    return image_name.lower().endswith((".png", ".jpg", ".jpeg", ".tif", ".tiff"))


def check_if_approved_image_format(image_ext):
    return image_ext in ("PNG", "JPG", "JPEG", "TIFF")


def _get_growth_stage_names():
    global __GROWTH_STAGE_NAMES
    try:
        return __GROWTH_STAGE_NAMES
    except NameError:
        pass
    data_path = pathlib.Path(__file__).parent / "growth_stage_labels.json"
    data = json.load(open(data_path))
    out = {}
    # JSON requires string keys
    out["fine"] = {int(k): v for k, v in data.pop("fine").items()}
    for scheme, ranges in data.items():
        out[scheme] = {}
        for range_ in ranges:
            for i in range(range_["lo"], range_["hi"] + 1):
                out[scheme][i] = range_["label"]
    __GROWTH_STAGE_NAMES = out
    return out


def lookup_growth_stage_name(idx, scheme):
    valid = ["fine", "bbch_ranges", "grain_ranges"]
    if scheme not in valid:
        raise ValueError(f"scheme must be one of {valid}. Got {scheme}")
    return _get_growth_stage_names()[scheme][idx]


def get_task_types(annotations):
    if not annotations:
        return set()
    if hasattr(annotations, "items"):
        annotations = [annotations]
    out = {"classification"}
    for annotation in annotations:
        if annotation.get("segmentation"):  # empty segmentation should not be counted
            out.add("segmentation")
            # FIXME: should we be assuming that one should turn segmentation into bbox?
            out.add("bounding box")
        if "bbox" in annotation:
            out.add("bounding box")
    return out


def get_supercategory_names(name):
    if not name.startswith("weed: "):
        return []

    species = name.split(": ", 1)[1]
    out = ["weed"]
    if species == "UNSPECIFIED":
        return out

    eppo = get_eppo_singleton(EPPO_PATH)
    try:
        entry = eppo.lookup_preferred_name(species, species_only=False)
    except Exception:
        warnings.warn(f"Failed to lookup species {repr(species)}")
        return out

    try:
        family = next(
            code for code in entry["ancestors"] if code.endswith(eppo.FAMILY_SUFFIX)
        )
    except StopIteration:
        family = None
    if family != "1GRAF":
        out.append("weed: non-poaceae")

    if family is not None:
        family_entry = eppo.entries[family]
        out.append(f"weed: {family_entry['preferred_name'].lower()}")
    return out


def denormalise_weedcoco(weedcoco):
    """Puts objects into images from ID references

    E.g. "annotations" added to images and "category" to annotations

    Operates in-place.
    """
    id_lookup = {}
    for key, objs in weedcoco.items():
        for obj in objs:
            if "id" in obj:
                id_lookup[key, obj["id"]] = obj

    for annotation in weedcoco["annotations"]:
        image = id_lookup["images", annotation["image_id"]]
        image.setdefault("annotations", []).append(annotation)
        annotation["category"] = id_lookup["categories", annotation["category_id"]]

    for image in weedcoco["images"]:
        if "agcontext_id" in image:
            image["agcontext"] = id_lookup["agcontexts", image["agcontext_id"]]
