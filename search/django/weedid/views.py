from django.http import HttpResponse
from django.shortcuts import render
import requests
import os
import json
import traceback
from core.settings import UPLOAD_DIR, REPOSITORY_DIR, MAX_IMAGE_SIZE, SITE_BASE_URL
from weedid.tasks import submit_upload_task, update_index_and_thumbnails
from weedid.utils import (
    store_tmp_weedcoco,
    setup_upload_dir,
    store_tmp_image,
    create_upload_entity,
    retrieve_listing_info,
    remove_entity_local_record,
    set_categories,
    add_agcontexts,
    add_metadata,
    retrieve_category_name,
)
from weedid.models import Dataset, WeedidUser
from weedcoco.validation import validate, JsonValidationError
from django.contrib.auth import login, logout
from django.contrib.auth.hashers import check_password
from django.http import (
    HttpResponseForbidden,
    HttpResponseNotAllowed,
    HttpResponseBadRequest,
)
from django.views.decorators.csrf import ensure_csrf_cookie


@ensure_csrf_cookie
def set_csrf(request):
    return HttpResponse("Success")


def elasticsearch_query(request):
    try:
        elasticsearch_url = "/".join(request.path.split("/")[2:])
    except Exception:
        return HttpResponseBadRequest("Invalid query format")
    if not elasticsearch_url.startswith("weedid/_msearch"):
        return HttpResponseBadRequest("Only _msearch queries are currently forwarded")
    if request.method not in ["POST", "GET"]:
        return HttpResponseNotAllowed(request.method)
    elasticsearch_response = requests.post(
        url=f"http://elasticsearch:9200/{elasticsearch_url}",
        data=request.body,
        headers=request.headers,
    )
    return HttpResponse(elasticsearch_response)


def upload(request):
    if not request.method == "POST":
        return HttpResponseNotAllowed(request.method)
    user = request.user
    if not (user and user.is_authenticated):
        return HttpResponseForbidden("You dont have access to proceed")
    try:
        images = []
        file_weedcoco = request.FILES["weedcoco"]
        weedcoco_json = json.load(file_weedcoco)
        validate(
            weedcoco_json,
            schema=request.POST["schema"]
            if request.POST["schema"]
            else "compatible-coco",
        )
        for image_reference in weedcoco_json["images"]:
            images.append(image_reference["file_name"].split("/")[-1])
        categories = [
            retrieve_category_name(category) for category in weedcoco_json["categories"]
        ]
        upload_dir, upload_id = setup_upload_dir(os.path.join(UPLOAD_DIR, str(user.id)))
        weedcoco_path = store_tmp_weedcoco(file_weedcoco, upload_dir)
        create_upload_entity(weedcoco_path, upload_id, user.id)
    except JsonValidationError as e:
        traceback.print_exc()
        return HttpResponseBadRequest(json.dumps(e.get_error_details()))
    except Exception as e:
        traceback.print_exc()
        return HttpResponseBadRequest(str(e))
    else:
        return HttpResponse(
            json.dumps(
                {"upload_id": upload_id, "images": images, "categories": categories}
            )
        )


def upload_image(request):
    if not request.method == "POST":
        return HttpResponseNotAllowed(request.method)
    user = request.user
    if not (user and user.is_authenticated):
        return HttpResponseForbidden("You dont have access to proceed")
    upload_id = request.POST["upload_id"]
    upload_image = request.FILES["upload_image"]
    if upload_image.size > MAX_IMAGE_SIZE:
        return HttpResponseBadRequest("This image has exceeded the size limit!")
    upload_dir = os.path.join(UPLOAD_DIR, str(user.id), upload_id, "images")
    store_tmp_image(upload_image, upload_dir)
    return HttpResponse(f"Uploaded {upload_image.name} to {upload_dir}")


def update_categories(request):
    if not request.method == "POST":
        return HttpResponseNotAllowed(request.method)
    user = request.user
    if not (user and user.is_authenticated):
        return HttpResponseForbidden("You dont have access to proceed")
    data = json.loads(request.body)
    upload_id, categories = data["upload_id"], data["categories"]
    weedcoco_path = os.path.join(
        UPLOAD_DIR, str(user.id), str(upload_id), "weedcoco.json"
    )
    try:
        set_categories(weedcoco_path, categories)
    except Exception:
        return HttpResponseNotAllowed("Failed to update categories")
    else:
        return HttpResponse(
            f"Updated categories for user {user.id}'s upload{upload_id}"
        )


def upload_agcontexts(request):
    if not request.method == "POST":
        return HttpResponseNotAllowed(request.method)
    user = request.user
    if not (user and user.is_authenticated):
        return HttpResponseForbidden("You dont have access to proceed")
    data = json.loads(request.body)
    upload_id, ag_contexts = data["upload_id"], data["ag_contexts"]
    weedcoco_path = os.path.join(
        UPLOAD_DIR, str(user.id), str(upload_id), "weedcoco.json"
    )
    try:
        add_agcontexts(weedcoco_path, ag_contexts)
        Dataset.objects.filter(upload_id=upload_id).update(agcontext=[ag_contexts])
    except Exception:
        return HttpResponseNotAllowed("Failed to add AgContexts")
    else:
        return HttpResponse(
            f"Updated AgContexts for user {user.id}'s upload{upload_id}"
        )


def upload_metadata(request):
    if request.method == "POST":
        user = request.user
        if user and user.is_authenticated:
            data = json.loads(request.body)
            upload_id, metadata = data["upload_id"], data["metadata"]
            weedcoco_path = os.path.join(
                UPLOAD_DIR, str(user.id), str(upload_id), "weedcoco.json"
            )
            try:
                add_metadata(weedcoco_path, metadata)
                Dataset.objects.filter(upload_id=upload_id).update(metadata=metadata)
            except Exception:
                return HttpResponseNotAllowed("Failed to add Metadata")
            else:
                return HttpResponse(
                    f"Updated Metadata for user {user.id}'s upload{upload_id}"
                )
        else:
            return HttpResponseForbidden("You dont have access to proceed")
    else:
        return HttpResponseNotAllowed(request.method)


def submit_deposit(request):
    if not request.method == "POST":
        return HttpResponseNotAllowed(request.method)
    user = request.user
    if not (user and user.is_authenticated):
        return HttpResponseForbidden("You dont have access to proceed")
    upload_id = request.POST["upload_id"]
    weedcoco_path = os.path.join(
        UPLOAD_DIR, str(user.id), str(upload_id), "weedcoco.json"
    )
    images_dir = os.path.join(UPLOAD_DIR, str(user.id), str(upload_id), "images")
    submit_upload_task.delay(weedcoco_path, images_dir, upload_id)
    return HttpResponse(f"Work on user {user.id}'s upload{upload_id}")


def upload_status(request):
    user = request.user
    if not (user and user.is_authenticated):
        return HttpResponse("You havent been logged in")
    user_id = request.user.id
    upload_entity = WeedidUser.objects.get(id=user_id).latest_upload
    return HttpResponse(
        json.dumps(
            {
                "upload_status": upload_entity.status,
                "upload_status_details": upload_entity.status_details,
            }
        )
    )


def upload_info(request, dataset_id):
    if request.method != "GET":
        return HttpResponseNotAllowed(request.method)
    upload_entity = Dataset.objects.get(upload_id=dataset_id)
    return HttpResponse(
        json.dumps(
            {"metadata": upload_entity.metadata, "agcontexts": upload_entity.agcontext}
        )
    )


def upload_list(request):
    upload_list = [
        retrieve_listing_info(dataset, awaiting_review=False)
        for dataset in Dataset.objects.filter(status="C")
    ]
    return HttpResponse(json.dumps(upload_list))


def awaiting_list(request):
    user = request.user
    if not (user and user.is_authenticated and user.is_staff):
        return HttpResponseForbidden("You dont have access to proceed")
    awaiting_list = [
        retrieve_listing_info(dataset, awaiting_review=True)
        for dataset in Dataset.objects.filter(status="AR")
    ]
    return HttpResponse(json.dumps(awaiting_list))


def dataset_approve(request, dataset_id):
    user = request.user
    if not (user and dataset_id and user.is_authenticated and user.is_staff):
        return HttpResponseForbidden("You dont have access to proceed")
    upload_entity = Dataset.objects.get(upload_id=dataset_id, status="AR")
    if upload_entity:
        weedcoco_path = os.path.join(REPOSITORY_DIR, str(dataset_id), "weedcoco.json")
        update_index_and_thumbnails(weedcoco_path, dataset_id)
        return HttpResponse("It has been approved")
    else:
        return HttpResponseNotAllowed("Dataset to be reviewed doesn't exist")


def dataset_reject(request, dataset_id):
    user = request.user
    if not (user and dataset_id and user.is_authenticated and user.is_staff):
        return HttpResponseForbidden("You dont have access to proceed")
    upload_entity = Dataset.objects.get(upload_id=dataset_id, status="AR")
    if upload_entity:
        try:
            remove_entity_local_record(str(upload_entity.user_id), str(dataset_id))
        finally:
            upload_entity.status = "F"
            upload_entity.status_details = "It failed to proceed after review."
            upload_entity.save()
        return HttpResponse("The dataset has been rejected and removed")
    else:
        return HttpResponseNotAllowed("Dataset to be rejected doesn't exist")


def user_register(request):
    if not request.method == "POST":
        return HttpResponseNotAllowed(request.method)
    username = request.POST["username"]
    email = request.POST["email"]
    password = request.POST["password"]
    try:
        user = WeedidUser.objects.create_user(username, email, password)
        user.save()
        return HttpResponse("The account has been created")
    except Exception:
        return HttpResponseForbidden("You dont have access to proceed")


def user_login(request):
    if not request.method == "POST":
        return HttpResponseNotAllowed(request.method)
    username = request.POST["username"]
    password = request.POST["password"]
    user = WeedidUser.objects.get(username=username)

    if user is not None and (
        user.password == password or check_password(password, user.password)
    ):
        login(request, user)
        return HttpResponse("You have been logged in")
    else:
        return HttpResponseForbidden("Wrong login credentials")


def user_logout(request):
    logout(request)
    return HttpResponse("You have been logged out")


def user_login_status(request):
    if request.user.is_authenticated:
        return HttpResponse("You have been logged in")
    else:
        return HttpResponseForbidden("You havent been logged in")


def login_google(request):
    if not request.method == "POST":
        return HttpResponseNotAllowed(request.method)
    body = json.loads(request.body)
    email, googleId = body["email"], body["googleId"]
    users = WeedidUser.objects.all().filter(email=email)
    if len(users) > 0:
        login(request, users[0])
        return HttpResponse("You have been logged in")
    else:
        user = WeedidUser.objects.create_user(email.split("@")[0], email, googleId)
        user.save()
        login(request, user)
        return HttpResponse("The account has been created and logged in")


def sitemap_xml(request):
    # roughly in order of SEO importance
    PATHS = [
        "/explore",
        "/datasets",
        "/editor",
        "/upload",
        "/about",
        "/weedcoco",
        "/meta-editor",
    ]
    urls = [{"loc": SITE_BASE_URL + path} for path in PATHS]
    for dataset in Dataset.objects.filter(status="C"):
        urls.append({"loc": SITE_BASE_URL + "/datasets/" + dataset.upload_id})
    return render(
        request, "sitemap.xml", context={"urls": urls}, content_type="text/xml"
    )
