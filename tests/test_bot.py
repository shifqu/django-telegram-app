"""Tests for the bot package."""

import uuid
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase

from django_telegram_app.bot import get_commands, load_command_class
from django_telegram_app.bot.testing.testcases import TelegramBotTestCase
from django_telegram_app.models import CallbackData, Message
from django_telegram_app.resolver import get_telegram_settings_model
from tests.testapps.samplebot.telegrambot.commands.echo import Command as EchoCommand
from tests.testapps.samplebot.telegrambot.commands.poll import Command as PollCommand


class BotTests(TelegramBotTestCase):
    """Tests for the bot package."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        super().setUpTestData()
        cls.user = get_user_model().objects.create_user(username="dummyuser", password="dummypass")
        cls.telegram_setting = get_telegram_settings_model().objects.create(user=cls.user, chat_id=123456789)

    def test_get_commands_returns_empty_dict_when_not_configured(self):
        """Test that get_commands returns an empty dict when settings are not configured."""
        get_commands.cache_clear()
        fake_settings = SimpleNamespace(configured=False)
        with patch("django_telegram_app.bot.settings", fake_settings):
            commands = get_commands()
        self.assertEqual(commands, {})

        # Ensure cache is cleared for other tests, otherwise none would find commands
        get_commands.cache_clear()

    def test_discovery_finds_poll_and_echo(self):
        """Test that the poll and echo commands are discovered and can be loaded."""
        expected_commands = {"poll": PollCommand, "echo": EchoCommand}
        for cmd, expected_class in expected_commands.items():
            assert cmd in get_commands().keys()

            appname = get_commands()[cmd]
            cmd_instance = load_command_class(appname, cmd, self.telegram_setting)
            assert isinstance(cmd_instance, expected_class)
            assert cmd_instance.get_command_string() == f"/{cmd}"

    def test_telegram_invalid_token(self):
        """Test the telegram app with an invalid token."""
        response = self.client.post(
            self.url,
            data={},
            headers={"X-Telegram-Bot-Api-Secret-Token": "invalid_token"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {"status": "error", "message": "Invalid token."})

    def test_telegram_send_help(self):
        """Test the telegram send help command.

        The help text should always be displayed when an unknown command/message/option is sent.
        """
        self.send_text("dummy text")
        self.assertEqual(self.fake_bot_post.call_count, 1)
        self.assertEqual(self.fake_bot_post.call_args.args[0], "sendMessage")
        self.assertIn("Currently available commands", self.fake_bot_post.call_args[1]["payload"]["text"])

    def test_poll_command(self):
        """Test the poll command."""
        self.send_text("/poll")
        self.click_on_text("🏓 Ping Pong")
        self.click_on_text("✅ Yes")
        expected_message_log = [
            "What is your favourite sport?",
            "Would you like to submit Ping Pong as your favourite sport?",
            "Thank you! Your favourite sport Ping Pong has been recorded.",
        ]
        self.verify_message_log(expected_message_log)

    def test_poll_command_next_page(self):
        """Test the next page functionality in the poll command."""
        self.send_text("/poll")
        self.click_on_text("➡️ Next")
        self.click_on_text("🥊 Boxing")
        self.click_on_text("✅ Yes")
        expected_message_log = [
            "What is your favourite sport?",
            "What is your favourite sport?",
            "Would you like to submit Boxing as your favourite sport?",
            "Thank you! Your favourite sport Boxing has been recorded.",
        ]
        self.verify_message_log(expected_message_log)

    def test_poll_command_cancel(self):
        """Test cancelling the poll command."""
        self.send_text("/poll")
        self.click_on_text("🤺 Fencing")
        self.click_on_text("❌ No")
        expected_message_log = [
            "What is your favourite sport?",
            "Would you like to submit Fencing as your favourite sport?",
            "Poll cancelled. Your favourite sport was not recorded.",
        ]
        self.verify_message_log(expected_message_log)

    def test_poll_command_previous(self):
        """Test using the previous button in the poll command."""
        self.send_text("/poll")
        self.click_on_text("🏸 Badminton")
        self.click_on_text("⬅️ Previous step")
        self.click_on_text("🤺 Fencing")
        self.click_on_text("✅ Yes")
        expected_message_log = [
            "What is your favourite sport?",
            "Would you like to submit Badminton as your favourite sport?",
            "What is your favourite sport?",
            "Would you like to submit Fencing as your favourite sport?",
            "Thank you! Your favourite sport Fencing has been recorded.",
        ]
        self.verify_message_log(expected_message_log)

    def test_echo_command(self):
        """Test the echo command."""
        self.send_text("/echo")
        self.send_text("Hello, World!")
        expected_message_log = [
            "Send the message you want to echo:",
            "You said: Hello, World!",
        ]
        self.verify_message_log(expected_message_log)

    def test_unknown_command(self):
        """Test sending an unknown command."""
        self.send_text("/unknowncommand")
        self.assertIn("Currently available commands", self.fake_bot_post.call_args[1]["payload"]["text"])

    def test_unexpected_error(self):
        """Test handling an unexpected error in a command."""
        with patch("django_telegram_app.bot.bot.handle_update", MagicMock()) as fake_bot_handle_update:
            fake_bot_handle_update.side_effect = Exception("Simulated error")
            response = self.send_text("/whatever", verify=False)
        self.assertEqual(response.json(), {"status": "error", "message": "Message received."})
        last_message = Message.objects.last()
        assert last_message is not None  # Use assertion to satisfy type checker
        assert last_message.error is not None  # Use assertion to satisfy type checker
        self.assertIn("Simulated error", last_message.error)

    def test_token_is_valid_if_not_configured(self):
        """Test that any token is valid if BOT_API_SECRET_TOKEN is not configured."""
        with patch("django_telegram_app.bot.bot.settings.WEBHOOK_TOKEN", ""):
            response = self.client.post(
                self.url,
                data={},
                headers={"X-Telegram-Bot-Api-Secret-Token": "any_token"},
                content_type="application/json",
            )
        self.assertEqual(response.status_code, 200)

    def test_call_command_step_do_nothing(self):
        """Test that calling a command step with token DO_NOTHING it does nothing."""
        from django_telegram_app.bot.bot import DO_NOTHING, _call_command_step

        called = _call_command_step(DO_NOTHING, MagicMock(), MagicMock())
        self.assertFalse(called)

    def test_call_command_step_callback_not_found(self):
        """Test that calling a command step with an invalid token raises."""
        from django_telegram_app.bot.bot import _call_command_step

        uuid_token = str(uuid.uuid4())
        CallbackData.objects.filter(token=uuid_token).delete()  # Ensure it does not exist
        called = _call_command_step(uuid_token, MagicMock(), MagicMock())
        self.assertFalse(called)

    def test_command_has_steps_abstract(self):
        """Test that accessing steps property on BaseCommand raises NotImplementedError."""
        from django_telegram_app.bot.base import BaseCommand

        command = BaseCommand(MagicMock())
        with self.assertRaises(NotImplementedError):
            _ = command.steps

    def test_step_handle_abstract(self):
        """Test that calling handle method on Step raises NotImplementedError."""
        from django_telegram_app.bot.base import Step

        step = Step(MagicMock())
        with self.assertRaises(NotImplementedError):
            step.handle(MagicMock())


class ExtraBotTests(SimpleTestCase):
    """Extra tests for bot functions which are mocked in BotTests."""

    def test_post(self):
        """Test the post function sends a request to the correct endpoint."""
        from django_telegram_app.bot.bot import post

        with patch("django_telegram_app.bot.bot.requests.post") as fake_requests_post:
            endpoint = "sendMessage"
            payload = {"chat_id": 123456789, "text": "Hello"}
            post(endpoint, payload)

            fake_requests_post.assert_called_once_with(
                "https://api.telegram.org/bot123:abc/sendMessage", json=payload, timeout=5
            )
