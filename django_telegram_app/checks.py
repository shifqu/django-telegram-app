"""Checks for the telegram app."""

from django.core.checks import Error, register
from django.core.exceptions import ImproperlyConfigured

from django_telegram_app import get_telegram_settings_model
from django_telegram_app.bot import get_commands
from django_telegram_app.conf import settings
from django_telegram_app.models import AbstractTelegramSettings


@register()
def check_telegram_required_settings(app_configs, **kwargs):  # noqa: ARG001  # pylint: disable=unused-argument
    """Check that all required TELEGRAM settings are present."""
    errors = []
    missing = settings.missing_settings()
    if missing:
        errors.append(
            Error(
                f"Missing required TELEGRAM settings: {', '.join(missing)}",
                hint="Add the missing settings in settings.py under the TELEGRAM key.",
                id="telegram.E001",
            )
        )
    return errors


@register()
def check_swappable_telegram_settings(app_configs, **kwargs):  # noqa: ARG001  # pylint: disable=unused-argument
    """Check that TELEGRAM_SETTINGS_MODEL resolves correctly and is a subclass of AbstractTelegramSettings."""
    errors = []

    try:
        model = get_telegram_settings_model()
    except ImproperlyConfigured as exc:
        errors.append(
            Error(
                str(exc),
                hint="Ensure TELEGRAM_SETTINGS_MODEL is defined correctly or omit it to use the default.",
                id="telegram.E002",
            )
        )
        return errors
    except Exception as exc:  # just in case of unexpected errors
        errors.append(
            Error(
                f"Unexpected error while resolving TELEGRAM_SETTINGS_MODEL: {exc!r}",
                id="telegram.E003",
            )
        )
        return errors

    # If resolution succeeded, ensure it subclasses AbstractTelegramSettings
    if not issubclass(model, AbstractTelegramSettings):
        errors.append(
            Error(
                f"{model._meta.label} must subclass telegram.models.base.AbstractTelegramSettings.",
                hint="Update your custom model to inherit from the abstract base.",
                id="telegram.E004",
            )
        )

    return errors


@register()
def check_get_commands(app_configs, **kwargs):  # noqa: ARG001  # pylint: disable=unused-argument
    """Check that get_commands() can load all command classes without errors.

    Since get_commands() is cached, this check also serves to warm the cache.
    """
    errors = []
    try:
        get_commands()
    except Exception as exc:
        errors.append(
            Error(
                f"Error loading commands: {exc!r}",
                hint="Ensure the command modules are defined correctly.",
                id="telegram.E005",
            )
        )
    return errors
