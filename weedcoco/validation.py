"""Validation tools for WeedCOCO
"""
import pathlib
import argparse
import sys
import json

import jsonschema
import yaml

SCHEMA_DIR = pathlib.Path(__file__).parent / "schema"
MAIN_SCHEMA_URI = "https://weedid.sydney.edu.au/schema/main.json"


class ValidationError(Exception):
    pass


def validate_json(weedcoco, schema_dir=SCHEMA_DIR):
    """Check that the weedcoco matches its JSON schema"""
    try:
        # memoise the schema
        ref_store = validate_json.ref_store
    except AttributeError:
        schema_objects = [
            yaml.safe_load(path.open()) for path in SCHEMA_DIR.glob("*.yaml")
        ]
        validate_json.ref_store = {obj["$id"]: obj for obj in schema_objects}
        ref_store = validate_json.ref_store
    main_schema = ref_store[MAIN_SCHEMA_URI]
    jsonschema.validate(
        weedcoco,
        schema=main_schema,
        resolver=jsonschema.RefResolver(MAIN_SCHEMA_URI, main_schema, store=ref_store),
    )


def validate_references(
    weedcoco,
    schema_dir=SCHEMA_DIR,
    require_reference=("collection", "image", "agcontext"),
):
    """Check that all IDs are unique and references valid"""
    known_ids = set()
    referenced_ids = set()

    # ensure IDs are unique per section
    for section_name, section in weedcoco.items():
        if section_name.endswith("s"):
            section_name_singular = section_name[:-1]
            if section_name.endswith("ies"):
                section_name_singular = section_name[:-3] + "y"
        else:
            section_name_singular = section_name
        if isinstance(section, list):
            for obj in section:
                if "id" not in obj:
                    # collection_memberships objects do not require 'id'
                    continue
                id_key = (section_name_singular, obj["id"])
                if id_key in known_ids:
                    raise ValidationError(f"Duplicate ID: {id_key}")
                else:
                    known_ids.add(id_key)

    # ensure referenced IDs are known
    # FIXME: this should be more precise, checking the relationship between
    # the referring and referent sections.
    for section_name, section in weedcoco.items():
        if isinstance(section, list):
            for obj in section:
                for key, val in obj.items():
                    if key.endswith("_id"):
                        id_key = (key[:-3], val)
                        if id_key not in known_ids:
                            raise ValidationError(
                                f"Reference to unknown ID: {id_key}. "
                                f"Found in {section_name} id {obj.get('id')}"
                            )
                        referenced_ids.add(id_key)

    for known_id in known_ids:
        section_name = known_id[0]
        if section_name in require_reference and known_id not in referenced_ids:
            raise ValidationError(f"{section_name} ID {known_id[1]} is unreferenced")
    # TODO: consider warning if not require_reference


def validate_coordinates(weedcoco):
    """Check that annotation coordinates are within the image"""
    image_lookup = {image["id"]: image for image in weedcoco["images"]}
    for annotation in weedcoco["annotations"]:
        width = image_lookup[annotation["image_id"]]["width"]
        height = image_lookup[annotation["image_id"]]["height"]
        if "bbox" in annotation:
            x, y, bbox_width, bbox_height = annotation["bbox"]
            if (
                x >= width
                or x + bbox_width > width
                or y >= height
                or y + bbox_height >= height
                or bbox_width == 0
                or bbox_height == 0
            ):
                raise ValidationError(
                    f"Invalid bounding box dimensions: "
                    f"x1={x}, y1={y}, x2={x + bbox_width}, y2={y + bbox_width} "
                    f"must fit within image dimensions "
                    f"(w={width}, h={height}) "
                    f"and have non-zero area."
                )
        if "segmentation" in annotation and hasattr(
            annotation["segmentation"], "items"
        ):
            # RLE
            if annotation["segmentation"]["size"] != [width, height]:
                raise ValidationError(
                    f"Segmentation size {annotation['segmentation']['size']}"
                    f" does not match image size {[width, height]})"
                )
            if isinstance(annotation["segmentation"]["counts"], str):
                # TODO: determine if out of bounds
                pass
            else:
                n_pixels = sum(annotation["segmentation"]["counts"])
                if n_pixels > width * height:
                    raise ValidationError(
                        f"RLE-based segmentation is bigger "
                        f"than image of size {[width, height]}. "
                        f"Got counts summing to {n_pixels}"
                    )
        elif "segmentation" in annotation:
            # polygons
            for polygon in annotation["segmentation"]:
                if len(polygon) % 2 == 1:
                    raise ValidationError(
                        "Polygons must have an even number of elements"
                    )

            is_x = True
            for val in polygon:
                if val >= (width if is_x else height):
                    raise ValidationError(
                        f"Polygon coordinate out of bounds: "
                        f"{val} >= {'width' if is_x else 'height'}="
                        f"{width if is_x else height}"
                    )

        # TODO: check area within tolerance


def validate_image_sizes(weedcoco, images_root):
    """Check that all image sizes match the image files"""
    # TODO


def validate(weedcoco, images_root=None):
    if hasattr(weedcoco, "read"):
        weedcoco = json.load(weedcoco)
    validate_json(weedcoco)
    validate_references(weedcoco)
    validate_coordinates(weedcoco)
    if images_root is not None:
        validate_image_sizes(weedcoco, images_root)


def main():
    ap = argparse.ArgumentParser("WeedCOCO Validator")
    ap.add_argument("paths", nargs="+", type=argparse.FileType("r"))
    ap.add_argument(
        "--images-root", default=".", help="Root for image file names. Default=."
    )
    ap.add_argument(
        "--disable-size-check",
        action="store_const",
        dest="images_root",
        const=None,
        help="Disable validating image sizes are correct, which requires paths to be valid",
    )
    args = ap.parse_args()
    for path in args.paths:
        try:
            validate(path, images_root=args.images_root)
        except Exception:
            print(f"While validating {path}", file=sys.stderr)
            raise


if __name__ == "__main__":
    main()
