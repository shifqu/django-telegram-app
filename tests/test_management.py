"""Tests for the management package."""

from io import StringIO
from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.core.management.base import CommandError

from django_telegram_app import get_telegram_settings_model
from django_telegram_app.bot.testing.testcases import TelegramBotTestCase

SETWEBHOOK_PATH = "django_telegram_app.management.commands.setwebhook"


class ManagementCommandTests(TelegramBotTestCase):
    """Tests for management commands."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.telegram_setting = get_telegram_settings_model().objects.create(chat_id=123456789)

    def test_base_management_command_runs(self):
        """Test that the BaseManagementCommand can be invoked without errors."""
        out = StringIO()
        call_command("poll", stdout=out)

    def test_base_management_command_checks_command_attribute(self):
        """Test that poll raises if the 'command' attribute is None."""
        # Patch samplebot's poll command to None to trigger ValueError
        out = StringIO()
        with self.assertRaises(ValueError):
            with patch("tests.testapps.samplebot.management.commands.poll.Command.command", None):
                call_command("poll", stdout=out)

    def test_base_management_command_respects_force_and_should_run(self):
        """Test that the --force option works as expected.

        force=False, should_run=False -> no output
        force=True, should_run=False -> output expected
        force=False, should_run=True -> output expected
        force=True, should_run=True -> output expected
        """
        with patch("tests.testapps.samplebot.management.commands.poll.Command.should_run", return_value=False):
            out = StringIO()
            call_command("poll", force=False, stdout=out)
            self.assertIn("Command '/poll' skipped as `should_run` returned False.", out.getvalue())
            out = StringIO()
            call_command("poll", force=True, stdout=out)
            self.assertIn(f"Started poll for {self.telegram_setting}.", out.getvalue())
            self.assertNotIn("No Telegram-settings found for the given filter. Nothing to do.", out.getvalue())

        with patch("tests.testapps.samplebot.management.commands.poll.Command.should_run", return_value=True):
            out = StringIO()
            call_command("poll", force=False, stdout=out)
            self.assertIn(f"Started poll for {self.telegram_setting}.", out.getvalue())
            out = StringIO()
            call_command("poll", force=True, stdout=out)
            self.assertIn(f"Started poll for {self.telegram_setting}.", out.getvalue())

        self.telegram_setting.delete()
        out = StringIO()
        call_command("poll", force=True, stdout=out)
        self.assertIn("No Telegram-settings found for the given filter. Nothing to do.", out.getvalue())

    def test_set_webhook_command(self):
        """Test that the set_webhook command runs without errors."""
        out = StringIO()
        # Patch requests.post to avoid real HTTP calls
        with patch(f"{SETWEBHOOK_PATH}.requests.post") as fake_post:
            fake_post.return_value.status_code = 200
            fake_post.return_value.json.return_value = {"ok": True, "result": True}
            call_command("setwebhook", "https://example.com", stdout=out)
        self.assertIn("Successfully set webhook to", out.getvalue())

    def test_set_webhook_command_no_token(self):
        """Test that the set_webhook command runs without errors."""
        out = StringIO()
        # Patch requests.post to avoid real HTTP calls
        with patch(f"{SETWEBHOOK_PATH}.requests.post") as fake_post:
            with patch(f"{SETWEBHOOK_PATH}.app_settings.WEBHOOK_TOKEN", ""):
                fake_post.return_value.status_code = 200
                fake_post.return_value.json.return_value = {"ok": True, "result": True}
                call_command("setwebhook", "https://example.com", stdout=out)
        self.assertIn("Successfully set webhook to", out.getvalue())

    def test_set_webhook_command_failure(self):
        """Test that the set_webhook command handles failure correctly."""
        out = StringIO()
        err = StringIO()
        # Patch requests.post to simulate a failure response
        with patch(f"{SETWEBHOOK_PATH}.requests.post") as fake_post:
            fake_post.return_value.status_code = 200
            fake_post.return_value.json.return_value = {"ok": False, "description": "Invalid URL"}
            with self.assertRaises(CommandError, msg="Failed to set webhook to"):
                call_command("setwebhook", "https://example.com", stdout=out, stderr=err)
            self.assertEqual(out.getvalue(), "")
            self.assertIn("Something went wrong while setting the webhook", err.getvalue())

    def test_setcommands(self):
        """Test that the setcommands command runs without errors."""
        out = StringIO()
        # Patch requests.post to avoid real HTTP calls
        with patch("django_telegram_app.management.commands.setcommands.requests.post") as fake_post:
            fake_post.return_value.status_code = 200
            fake_post.return_value.json.return_value = {"ok": True, "result": True}
            call_command("setcommands", stdout=out)
        self.assertIn("Successfully called setMyCommands.", out.getvalue())
        with self.assertRaises(KeyError, msg="language_code"):
            self._get_language_codes(fake_post)

    def test_setcommands_single_locale(self):
        """Test that the setcommands command runs without errors for a single locale."""
        out = StringIO()
        # Patch requests.post to avoid real HTTP calls
        with patch("django_telegram_app.management.commands.setcommands.requests.post") as fake_post:
            fake_post.return_value.status_code = 200
            fake_post.return_value.json.return_value = {"ok": True, "result": True}
            call_command("setcommands", "--locale=en", stdout=out)
        self.assertIn("Successfully called setMyCommands.", out.getvalue())
        self.assertEqual(["en"], self._get_language_codes(fake_post))

    def test_setcommands_multi_locale(self):
        """Test that the setcommands command runs without errors for multiple locales."""
        out = StringIO()
        # Patch requests.post to avoid real HTTP calls
        with patch("django_telegram_app.management.commands.setcommands.requests.post") as fake_post:
            fake_post.return_value.status_code = 200
            fake_post.return_value.json.return_value = {"ok": True, "result": True}
            call_command("setcommands", "--locale=en", "--locale=nl", stdout=out)
        self.assertIn("Successfully called setMyCommands.", out.getvalue())
        self.assertEqual(["en", "nl"], self._get_language_codes(fake_post))

    def test_setcommands_delete(self):
        """Test that the setcommands command runs without errors for deleting commands."""
        out = StringIO()
        # Patch requests.post to avoid real HTTP calls
        with patch("django_telegram_app.management.commands.setcommands.requests.post") as fake_post:
            fake_post.return_value.status_code = 200
            fake_post.return_value.json.return_value = {"ok": True, "result": True}
            call_command("setcommands", "--delete", stdout=out)
        self.assertIn("Successfully called deleteMyCommands.", out.getvalue())

    def test_setcommands_delete_with_locale(self):
        """Test that the setcommands command runs without errors for deleting commands with locale supplied."""
        out = StringIO()
        # Patch requests.post to avoid real HTTP calls
        with patch("django_telegram_app.management.commands.setcommands.requests.post") as fake_post:
            fake_post.return_value.status_code = 200
            fake_post.return_value.json.return_value = {"ok": True, "result": True}
            call_command("setcommands", "--delete", "--locale=en", stdout=out)
        self.assertIn("Successfully called deleteMyCommands.", out.getvalue())
        self.assertEqual(["en"], self._get_language_codes(fake_post))

    def test_setcommands_include_hidden(self):
        """Test that the setcommands command runs without errors including hidden commands."""
        out = StringIO()
        # Patch requests.post to avoid real HTTP calls
        with patch("django_telegram_app.management.commands.setcommands.requests.post") as fake_post:
            fake_post.return_value.status_code = 200
            fake_post.return_value.json.return_value = {"ok": True, "result": True}
            call_command("setcommands", "--include-hidden", stdout=out)
        self.assertIn("Successfully called setMyCommands.", out.getvalue())

        command_names = self._get_command_names(fake_post)
        self.assertIn("hiddencommand", command_names)
        self.assertIn("hiddencommand", command_names)

    def test_setcommands_failing_post(self):
        """Test that the setcommands command properly errors when post fails."""
        out = StringIO()
        # Patch requests.post to avoid real HTTP calls
        with patch("django_telegram_app.management.commands.setcommands.requests.post") as fake_post:
            fake_post.return_value.status_code = 200
            fake_post.return_value.json.return_value = {"ok": False, "result": True}
            with self.assertRaises(CommandError, msg="Something went wrong while calling"):
                call_command("setcommands", "--include-hidden", stdout=out)

    def _get_command_names(self, fake_post: MagicMock):
        return [cmd["command"] for cmd in fake_post.call_args[1]["json"]["commands"]]

    def _get_language_codes(self, fake_post: MagicMock):
        return [call_arg[1]["json"]["language_code"] for call_arg in fake_post.call_args_list]
