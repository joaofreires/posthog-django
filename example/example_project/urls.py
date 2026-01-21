from django.urls import path
from example_app import views

urlpatterns = [
    path("", views.index, name="index"),
    path("flags/", views.flags, name="flags"),
    path("error/", views.error, name="error"),
    path("middleware-error/", views.middleware_captured_error, name="middleware_error"),
]
