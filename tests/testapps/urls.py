"""URLs for test project."""

from django.urls import include, path

from django_telegram_app.conf import settings as telegram_app_settings

urlpatterns = [
    path(telegram_app_settings.ROOT_URL, include("django_telegram_app.urls")),
]
