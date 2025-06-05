from django.contrib import admin
from django.urls import path
from myproject.views import whoami, login_view

urlpatterns = [
    path("login/", login_view),
    path("whoami/", whoami),
]
