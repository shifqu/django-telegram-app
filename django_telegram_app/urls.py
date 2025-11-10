"""URL configuration for telegram app."""

from django.urls import path

from django_telegram_app import views
from django_telegram_app.conf import settings

urlpatterns = [
    path(settings.WEBHOOK_URL, views.webhook, name="webhook"),
]
