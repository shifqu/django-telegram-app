"""Sample app configuration."""

from django.apps import AppConfig


class SampleBotConfig(AppConfig):
    """Sample bot app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "tests.testapps.samplebot"
    label = "tests_samplebot"
