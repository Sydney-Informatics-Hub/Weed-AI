from django.urls import path, re_path
from weedid import views

urlpatterns = [
    path("api/test/", views.test, name="test"),
    path("api/upload/", views.upload, name="upload"),
    path("api/upload_image/", views.upload_image, name="upload_image"),
    path("api/submit_deposit/", views.submit_deposit, name="submit_deposit"),
    path("api/upload_status/", views.upload_status, name="upload_status"),
    path("api/upload_info/", views.upload_info, name="upload_info"),
    path("api/upload_list/", views.upload_list, name="upload_list"),
    path("api/register/", views.user_register, name="user_register"),
    path("api/login/", views.user_login, name="user_login"),
    path("api/logout/", views.user_logout, name="user_logout"),
    path("api/login_status/", views.user_login_status, name="user_login_status"),
    re_path(r"^elasticsearch", views.elasticsearch_query, name="elasticsearch_query"),
]
