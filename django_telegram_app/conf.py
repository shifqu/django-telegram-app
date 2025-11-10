"""Telegram configuration."""

from django.conf import settings as django_settings

DEFAULTS = {
    "ROOT_URL": "telegram/",
    "WEBHOOK_URL": "webhook",
    "USER_LANGUAGE_ATTRS": ("language", "lang", "preferred_language"),
    "WEBHOOK_TOKEN": "",
}
REQUIRED = ["BOT_URL"]


class AppSettings:
    """Telegram app settings."""

    def __init__(self):
        """Initialize the settings."""
        user_settings = getattr(django_settings, "TELEGRAM", {}) or {}
        merged_settings = {**DEFAULTS, **user_settings}
        self._settings = merged_settings

    def __getattr__(self, name):
        """Get a setting by name."""
        return self._settings[name]

    def missing_settings(self):
        """Return a list of missing required settings."""
        return [k for k in REQUIRED if k not in self._settings]


settings = AppSettings()
