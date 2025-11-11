"""Tests to verify that django_telegram_app is configured correctly."""

import importlib

from django.test import SimpleTestCase


class AppsTests(SimpleTestCase):
    """Tests for django_telegram_app apps module."""

    def test_import_and_urls(self):
        """Test that the package can be imported and URLs are present."""
        import django_telegram_app  # noqa: F401

        mod = importlib.import_module("django_telegram_app.urls")
        assert hasattr(mod, "urlpatterns")
