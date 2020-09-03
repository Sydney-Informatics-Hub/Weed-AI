#!/usr/bin/env python
# coding: utf-8
# Exports Weed COCO on stdin to ElasticSearch _bulk data on stdout

import sys
import json
import argparse
import os
import logging

log = logging.getLogger()
logging.basicConfig(level=logging.INFO)

ap = argparse.ArgumentParser()
ap.add_argument(
    "--thumbnail-dir", help="Replace the input file_name directory with this"
)
args = ap.parse_args()

coco = json.load(sys.stdin)
del coco["info"]
try:
    del coco["collection_memberships"]
except KeyError:
    pass

id_lookup = {}
for key, objs in coco.items():
    log.info(f"Mapping {len(objs)} {key}")
    for obj in objs:
        id_lookup[key, obj["id"]] = obj


def _flatten(src, dst, prefix):
    for k, v in src.items():
        dst[f"{prefix}__{k}"] = v


for annotation in coco["annotations"]:
    image = id_lookup["images", annotation["image_id"]]
    image.setdefault("annotations", []).append(annotation)
    annotation["category"] = id_lookup["categories", annotation["category_id"]]
    _flatten(annotation["category"], annotation, "category")
    # todo: add collection from collection_memberships
    if hasattr(args, "thumbnail_dir"):
        image["thumbnail"] = (
            args.thumbnail_dir + "/" + os.path.basename(image["file_name"])
        )
    else:
        image["thumbnail"] = image["file_name"]

for image in coco["images"]:
    image["agcontext"] = id_lookup["agcontexts", image["agcontext_id"]]
    _flatten(image["agcontext"], image, "agcontext")
    # todo: add license
    for annotation in image["annotations"]:
        for k in annotation:
            image.setdefault(f"annotation__{k}", []).append(annotation[k])

f = sys.stdout
f.write("\n")
for image in coco["images"]:
    json.dump({"index": {"_index": "weedid", "_type": "image"}}, f)
    f.write("\n")
    json.dump(image, f)
    f.write("\n")
