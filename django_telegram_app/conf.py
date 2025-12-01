"""Telegram configuration."""

from django.conf import settings as django_settings
from django.utils.translation import gettext_lazy as _

DEFAULTS = {
    "ROOT_URL": "telegram/",
    "WEBHOOK_URL": "webhook",
    "WEBHOOK_TOKEN": "",
    "ALLOW_SETTINGS_CREATION_FROM_UPDATES": False,
    "REGISTER_DEFAULT_ADMIN": True,
    "HELP_TEXT_INTRO": _("Currently available commands:"),
    "HELP_RENDERER": None,
}
REQUIRED = ["BOT_URL"]


class AppSettings:
    """Telegram app settings."""

    def __init__(self):
        """Initialize the settings."""
        app_settings = getattr(django_settings, "TELEGRAM", {}) or {}
        merged_settings = {**DEFAULTS, **app_settings}
        self._settings = merged_settings

    def __getattr__(self, name):
        """Get a setting by name."""
        return self._settings[name]

    def missing_settings(self):
        """Return a list of missing required settings."""
        return [k for k in REQUIRED if k not in self._settings]


settings = AppSettings()
