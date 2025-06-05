from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from myproject.views import whoami

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name=None)),
    path("whoami/", whoami),
]
