import os
import json
from uuid import uuid4
from weedcoco.repo.deposit import mkdir_safely
from weedcoco.utils import set_info, set_licenses
from django.core.files.storage import FileSystemStorage
from weedid.models import Dataset, WeedidUser


def store_tmp_image(image, image_dir):
    fs = FileSystemStorage()
    fs.save(os.path.join(image_dir, image.name), image)


def store_tmp_weedcoco(weedcoco, upload_dir):
    fs = FileSystemStorage()
    weedcoco_path = os.path.join(upload_dir, weedcoco.name)
    fs.save(weedcoco_path, weedcoco)
    return weedcoco_path


def setup_upload_dir(upload_userid_dir):
    if not os.path.isdir(upload_userid_dir):
        mkdir_safely(upload_userid_dir)
    upload_id = str(uuid4())
    upload_dir = upload_userid_dir + f"/{upload_id}"
    mkdir_safely(upload_dir)
    return upload_dir, upload_id


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


def create_upload_entity(weedcoco_path, upload_id, upload_userid):
    upload_user = WeedidUser.objects.get(id=upload_userid)
    with open(weedcoco_path) as f:
        weedcoco_json = json.load(f)
    upload_entity = Dataset(
        upload_id=upload_id,
        agcontext=weedcoco_json["agcontexts"],
        user=upload_user,
        status="N",
        metadata={
            "info": weedcoco_json["info"],
            "license": weedcoco_json["license"],
            "collections": weedcoco_json["collections"],
        },
    )
    upload_entity.save()
    upload_user.latest_upload = upload_entity
    upload_user.save()
