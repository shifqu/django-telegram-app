"""Telegram app configuration."""

from django.apps import AppConfig


class TelegramConfig(AppConfig):
    """Represent the telegram AppConfig."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_telegram_app"
    label = "django_telegram_app"

    def ready(self):
        """Import checks."""
        import django_telegram_app.checks  # noqa: F401
