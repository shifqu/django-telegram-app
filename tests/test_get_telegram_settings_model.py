"""Tests for the get_telegram_settings function."""

from unittest.mock import patch

from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings

from django_telegram_app import get_telegram_settings_model


class GetModelTests(TestCase):
    """Tests for the get_telegram_settings function."""

    def test_get_telegram_settings_model_default(self):
        """Test that the default TelegramSettings model is returned when no custom model is set."""
        from django_telegram_app.models import TelegramSettings

        model = get_telegram_settings_model()
        self.assertEqual(model, TelegramSettings)

    @override_settings(TELEGRAM_SETTINGS_MODEL="tests_samplebot.CustomTelegramSettings")
    def test_get_telegram_settings_model_custom_model(self):
        """Test that a custom TelegramSettings model is returned when set."""
        from tests.testapps.samplebot.models import CustomTelegramSettings

        model = get_telegram_settings_model()
        self.assertEqual(model, CustomTelegramSettings)

    @override_settings(TELEGRAM_SETTINGS_MODEL="tests.DummyTelegramSettings")
    def test_get_telegram_settings_model_uninstalled_model(self):
        """Test that a custom TelegramSettings model is installed before use."""
        msg = "TELEGRAM_SETTINGS_MODEL refers to model 'tests.CustomTelegramSettings' that has not been installed"
        with self.assertRaises(ImproperlyConfigured, msg=msg):
            get_telegram_settings_model()

    @override_settings(TELEGRAM_SETTINGS_MODEL="invalid_format_model")
    def test_get_telegram_settings_model_invalid_format(self):
        """Test that an improperly formatted TELEGRAM_SETTINGS_MODEL raises an error."""
        msg = "TELEGRAM_SETTINGS_MODEL must be of the form 'app_label.model_name'"
        with self.assertRaises(ImproperlyConfigured, msg=msg):
            get_telegram_settings_model()

    @override_settings(TELEGRAM_SETTINGS_MODEL="tests_samplebot.CustomTelegramSettings")
    def test_get_telegram_settings_model_propagates_unhandled_exceptions(self):
        """Test that unhandled exceptions are propagated."""
        with patch.object(django_apps, "get_model", side_effect=RuntimeError("Unexpected error")):
            with self.assertRaises(RuntimeError, msg="Unexpected error"):
                get_telegram_settings_model()
