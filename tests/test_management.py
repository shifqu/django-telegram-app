"""Tests for the management package."""

from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError

from django_telegram_app import get_telegram_settings_model
from django_telegram_app.bot.testing.testcases import TelegramBotTestCase


class ManagementCommandTests(TelegramBotTestCase):
    """Tests for management commands."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.user = get_user_model().objects.create_user(username="dummyuser", password="dummypass")
        cls.telegram_setting = get_telegram_settings_model().objects.create(user=cls.user, chat_id=123456789)

    def test_base_telegram_command_runs(self):
        """Test that the BaseTelegramCommand can be invoked without errors."""
        out = StringIO()
        call_command("poll", stdout=out)

    def test_base_telegram_command_checks_command_attribute(self):
        """Test that the command raises if the 'command' attribute is None."""
        # Patch samplebot's poll command to None to trigger ValueError
        out = StringIO()
        with self.assertRaises(ValueError):
            with patch("tests.testapps.samplebot.management.commands.poll.Command.command", None):
                call_command("poll", stdout=out)

    def test_base_telegram_command_respects_force_and_should_run(self):
        """Test that the --force option works as expected.

        force=False, should_run=False -> no output
        force=True, should_run=False -> output expected
        force=False, should_run=True -> output expected
        force=True, should_run=True -> output expected
        """
        out = StringIO()

        with patch("tests.testapps.samplebot.management.commands.poll.Command.should_run", return_value=False):
            call_command("poll", force=False, stdout=out)
            self.assertIn("Command '/poll' skipped as should_run returned False.", out.getvalue())
            call_command("poll", force=True, stdout=out)
            self.assertIn(f"Started the command for {self.telegram_setting.user}.", out.getvalue())

        with patch("tests.testapps.samplebot.management.commands.poll.Command.should_run", return_value=True):
            call_command("poll", force=False, stdout=out)
            self.assertIn(f"Started the command for {self.telegram_setting.user}.", out.getvalue())
            call_command("poll", force=True, stdout=out)
            self.assertIn(f"Started the command for {self.telegram_setting.user}.", out.getvalue())

        self.telegram_setting.delete()
        call_command("poll", force=True, stdout=out)
        self.assertIn("No Telegram-enabled users found. Nothing to do.", out.getvalue())

    def test_get_user_language(self):
        """Test that the get_user_language function retrieves the correct language code."""
        from django.conf import settings

        from django_telegram_app.management.base import get_user_language

        user_no_lang = SimpleNamespace()
        lang = get_user_language(user_no_lang)
        self.assertEqual(lang, settings.LANGUAGE_CODE)

        user_fr = SimpleNamespace(language="fr")
        lang = get_user_language(user_fr)
        self.assertEqual(lang, "fr")

    def test_set_webhook_command(self):
        """Test that the set_webhook command runs without errors."""
        out = StringIO()
        # Patch requests.post to avoid real HTTP calls
        with patch("django_telegram_app.management.commands.setwebhook.requests.post") as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"ok": True, "result": True}
            call_command("setwebhook", stdout=out)
        self.assertIn("Successfully set webhook to", out.getvalue())

    def test_set_webhook_command_failure(self):
        """Test that the set_webhook command handles failure correctly."""
        out = StringIO()
        err = StringIO()
        # Patch requests.post to simulate a failure response
        with patch("django_telegram_app.management.commands.setwebhook.requests.post") as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"ok": False, "description": "Invalid URL"}
            with self.assertRaises(CommandError, msg="Failed to set webhook to"):
                call_command("setwebhook", stdout=out, stderr=err)
            self.assertEqual(out.getvalue(), "")
            self.assertIn("Something went wrong while setting the webhook", err.getvalue())
