"""Models for the sample bot app."""

from django.db import models

from django_telegram_app.models import AbstractTelegramSettings


class CustomTelegramSettings(AbstractTelegramSettings):
    """Custom Telegram settings model for testing."""

    extra_field = models.CharField(max_length=100, default="")
