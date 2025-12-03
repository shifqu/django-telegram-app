"""Tests for django_telegram_app checks."""

from unittest.mock import patch

from django.apps import apps
from django.core import checks
from django.test import SimpleTestCase, override_settings


class ChecksTests(SimpleTestCase):
    """Tests for django_telegram_app checks."""

    @staticmethod
    def run_telegram_checks():
        """Run telegram system checks and return the results."""
        return checks.run_checks(app_configs=[apps.get_app_config("django_telegram_app")])

    def test_checks_run_without_errors(self):
        """Test that system checks run without errors."""
        errors = self.run_telegram_checks()
        self.assertEqual(errors, [])

    def test_check_telegram_required_settings_missing_settings(self):
        """Test that an error is returned when settings are missing."""
        from django_telegram_app.conf import settings

        with patch.object(settings, "missing_settings", return_value=["BOT_URL"]):
            errors = self.run_telegram_checks()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].id, "telegram.E001")

    @override_settings(
        TELEGRAM_SETTINGS_MODEL="badformat",  # not app_label.ModelName
    )
    def test_check_swappable_telegram_settings_improperly_configured(self):
        """Test that an error is returned when TELEGRAM_SETTINGS_MODEL is improperly configured."""
        errors = self.run_telegram_checks()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].id, "telegram.E002")

    def test_check_swappable_telegram_settings_unexpected_error(self):
        """Test that an error is returned when an unexpected error occurs during model resolution."""
        with patch("django_telegram_app.checks.get_telegram_settings_model") as fake_get_model:
            fake_get_model.side_effect = Exception("Simulated error")
            errors = self.run_telegram_checks()

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].id, "telegram.E003")

    @override_settings(
        TELEGRAM_SETTINGS_MODEL="auth.User",  # installed, but wrong base class
    )
    def test_check_swappable_telegram_settings_wrong_base_class(self):
        """Test that an error is returned when TELEGRAM_SETTINGS_MODEL does not subclass AbstractTelegramSettings."""
        errors = self.run_telegram_checks()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].id, "telegram.E004")

    def test_check_get_commands_unexpected_error(self):
        """Test that an error is returned when an unexpected error occurs during command discovery."""
        with patch("django_telegram_app.checks.get_commands") as fake_get_commands:
            fake_get_commands.side_effect = Exception("Simulated error")
            errors = self.run_telegram_checks()

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].id, "telegram.E005")
