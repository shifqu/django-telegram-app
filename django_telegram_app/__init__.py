"""Telegram app."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

if TYPE_CHECKING:
    from django_telegram_app.models import AbstractTelegramSettings


def get_telegram_settings_model() -> type[AbstractTelegramSettings]:
    """Return the TelegramSettings model that is active in this project.

    If there is no custom model, return the default TelegramSettings model.
    """
    from django_telegram_app.models import AbstractTelegramSettings

    try:
        telegram_settings_model = settings.TELEGRAM_SETTINGS_MODEL
    except AttributeError:
        from django_telegram_app.models import TelegramSettings

        return TelegramSettings

    try:
        return cast(type[AbstractTelegramSettings], django_apps.get_model(telegram_settings_model, require_ready=False))
    except ValueError as exc:
        raise ImproperlyConfigured("TELEGRAM_SETTINGS_MODEL must be of the form 'app_label.model_name'") from exc
    except LookupError as exc:
        raise ImproperlyConfigured(
            f"TELEGRAM_SETTINGS_MODEL refers to model '{telegram_settings_model}' that has not been installed"
        ) from exc
