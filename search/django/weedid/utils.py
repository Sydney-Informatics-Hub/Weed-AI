import os
from shutil import rmtree
import json
from uuid import uuid4
import re
from weedcoco.repo.deposit import mkdir_safely
from weedcoco.utils import set_info, set_licenses
from weedcoco.stats import WeedCOCOStats
from django.core.files.storage import FileSystemStorage
from weedid.models import Dataset, WeedidUser
from core.settings import UPLOAD_DIR, REPOSITORY_DIR, DOWNLOAD_DIR


def store_tmp_image(image, image_dir):
    fs = FileSystemStorage()
    fs.save(os.path.join(image_dir, image.name), image)


def store_tmp_weedcoco(weedcoco, upload_dir):
    fs = FileSystemStorage()
    weedcoco_path = os.path.join(upload_dir, "weedcoco.json")
    fs.save(weedcoco_path, weedcoco)
    return weedcoco_path


def setup_upload_dir(upload_userid_dir):
    if not os.path.isdir(upload_userid_dir):
        mkdir_safely(upload_userid_dir)
    upload_id = str(uuid4())
    upload_dir = upload_userid_dir + f"/{upload_id}"
    mkdir_safely(upload_dir)
    return upload_dir, upload_id


def set_categories(weedcoco_path, categories):
    with open(weedcoco_path, "r") as jsonFile:
        data = json.load(jsonFile)
    new_categories = []
    for category in categories:
        if category["role"] and category["scientific_name"]:
            new_categories.append(
                {
                    "id": category["id"],
                    "name": ": ".join((category["role"], category["scientific_name"])),
                }
            )
        else:
            new_categories.append({"id": category["id"], "name": category["name"]})
    data["categories"] = new_categories
    with open(weedcoco_path, "w") as jsonFile:
        json.dump(data, jsonFile)


def add_agcontexts(weedcoco_path, ag_contexts):
    with open(weedcoco_path, "r") as jsonFile:
        data = json.load(jsonFile)
    data["agcontexts"] = [ag_contexts]
    for image in data["images"]:
        image["agcontext_id"] = ag_contexts["id"]
    with open(weedcoco_path, "w") as jsonFile:
        json.dump(data, jsonFile)


def add_metadata(weedcoco_path, metadata):
    with open(weedcoco_path, "r") as jsonFile:
        data = json.load(jsonFile)
    set_info(data, metadata)
    set_licenses(data)
    with open(weedcoco_path, "w") as jsonFile:
        json.dump(data, jsonFile)


def make_upload_entity_fields(weedcoco):
    category_to_name = {
        category["id"]: category["name"] for category in weedcoco["categories"]
    }

    stats = WeedCOCOStats(weedcoco)
    stats_with_cat_name = stats.category_summary.rename(
        index=category_to_name, level="category_id"
    )
    cat_counts_by_agcontext = dict(
        iter(stats_with_cat_name.groupby(level="agcontext_id"))
    )
    for agcontext in weedcoco["agcontexts"]:
        agcontext["n_images"] = int(
            stats.agcontext_summary.loc[agcontext["id"]].image_count
        )

        # Should produce something like:
        # {"crop: daucus carota": {"image_count": 1, "annotation_count": 1, "bounding_box_count": 1, "segmentation_count": 1}}
        # XXX: we use json.loads and to_json instead of to_dict, since to_dict
        #      was returning numpy.int64 numbers that could not be serialised.
        agcontext["category_statistics"] = json.loads(
            cat_counts_by_agcontext[agcontext["id"]]
            .droplevel("agcontext_id")
            .to_json(orient="index")
        )

    return {
        "agcontext": weedcoco["agcontexts"],
        "metadata": weedcoco["info"]["metadata"],
    }


def create_upload_entity(weedcoco_path, upload_id, upload_userid):
    upload_user = WeedidUser.objects.get(id=upload_userid)

    with open(weedcoco_path) as f:
        weedcoco_json = json.load(f)
    fields = make_upload_entity_fields(weedcoco_json)

    upload_entity = Dataset(upload_id=upload_id, user=upload_user, status="N", **fields)
    upload_entity.save()
    upload_user.latest_upload = upload_entity
    upload_user.save()


def remove_entity_local_record(user_id, upload_id):
    upload_dir_record = os.path.join(UPLOAD_DIR, user_id, upload_id)
    repository_dir_record = os.path.join(REPOSITORY_DIR, upload_id)
    download_dir_record = os.path.join(DOWNLOAD_DIR, f"{upload_id}.zip")
    for dir_path in [upload_dir_record, repository_dir_record, download_dir_record]:
        if os.path.isdir(dir_path):
            rmtree(dir_path, ignore_errors=True)
        elif os.path.isfile(dir_path):
            os.remove(dir_path)


def retrieve_listing_info(query_entity, awaiting_review):
    """Retrieving info from specific upload entity"""
    return {
        "name": query_entity.metadata["name"]
        if "name" in query_entity.metadata
        else "",
        "upload_id": query_entity.upload_id,
        "upload_date": str(query_entity.date),
        "contributor": query_entity.user.username,
        "contributor_email": query_entity.user.email if awaiting_review else "",
    }


def retrieve_category_name(category):
    if re.fullmatch(r"(crop|weed): .+", category["name"]):
        return {
            "id": category["id"],
            "name": category["name"],
            "role": category["name"].split(": ")[0],
            "scientific_name": category["name"].split(": ")[1],
        }
    else:
        return {
            "id": category["id"],
            "name": category["name"],
            "role": "",
            "scientific_name": "",
        }
