"""Tests for the bot package."""

import uuid
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from django_telegram_app import get_telegram_settings_model
from django_telegram_app.bot import get_commands, load_command_class
from django_telegram_app.bot.base import BaseBotCommand, Step
from django_telegram_app.bot.bot import DO_NOTHING, _call_command_step, _get_or_create_telegram_settings, send_help
from django_telegram_app.bot.testing.testcases import TelegramBotTestCase
from django_telegram_app.conf import settings
from django_telegram_app.models import CallbackData, Message
from tests.testapps.samplebot.telegrambot.commands.echo import Command as EchoCommand
from tests.testapps.samplebot.telegrambot.commands.hiddencommand import Command as HiddenCommand
from tests.testapps.samplebot.telegrambot.commands.poll import Command as PollCommand


class BotTests(TelegramBotTestCase):
    """Tests for the bot package."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.telegram_setting = get_telegram_settings_model().objects.create(chat_id=123456789)

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
        expected_commands = {"poll": PollCommand, "echo": EchoCommand, "hiddencommand": HiddenCommand}
        for cmd, expected_class in expected_commands.items():
            assert cmd in get_commands().keys()

            appname = get_commands()[cmd]
            cmd_instance = load_command_class(appname, cmd, self.telegram_setting)
            assert isinstance(cmd_instance, expected_class)
            assert cmd_instance.get_command_string() == f"/{cmd}"
        self.assertEqual(get_commands().keys(), expected_commands.keys())

    def test_telegram_invalid_token(self):
        """Test the telegram app with an invalid token."""
        response = self.client.post(
            self.webhook_url,
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
        self.assertIn("Currently available commands", self.last_bot_message)
        self.assertNotIn("hiddencommand", self.last_bot_message)

    def test_poll_command(self):
        """Test the poll command."""
        self.send_text("/poll")
        self.assertEqual(self.last_bot_message, "What is your favourite sport?")
        self.click_on_button("🏓 Ping Pong")
        self.assertEqual(self.last_bot_message, "Would you like to submit Ping Pong as your favourite sport?")
        self.click_on_button(0)  # First button is "✅ Yes"
        self.assertEqual(self.last_bot_message, "Thank you! Your favourite sport Ping Pong has been recorded.")

    def test_poll_command_next_page(self):
        """Test the next page functionality in the poll command."""
        self.send_text("/poll")
        self.assertEqual(self.last_bot_message, "What is your favourite sport?")
        self.click_on_button(-1)  # Last button is "➡️ Next page"
        self.assertEqual(self.last_bot_message, "What is your favourite sport?")
        self.click_on_button("🥊 Boxing")
        self.assertRegex(self.last_bot_message, "Would you like to submit Boxing as your favourite sport?")
        self.click_on_button("✅ Yes")
        self.assertEqual(self.last_bot_message, "Thank you! Your favourite sport Boxing has been recorded.")

    def test_poll_command_cancel(self):
        """Test cancelling the poll command."""
        self.send_text("/poll")
        self.assertEqual(self.last_bot_message, "What is your favourite sport?")
        self.click_on_button("🤺 Fencing")
        self.assertEqual(self.last_bot_message, "Would you like to submit Fencing as your favourite sport?")
        self.click_on_button("❌ No")
        self.assertEqual(self.last_bot_message, "Poll cancelled. Your favourite sport was not recorded.")

    def test_poll_command_previous(self):
        """Test using the previous button in the poll command."""
        self.send_text("/poll")
        self.assertEqual(self.last_bot_message, "What is your favourite sport?")
        self.click_on_button("🏸 Badminton")
        self.assertEqual(self.last_bot_message, "Would you like to submit Badminton as your favourite sport?")
        self.click_on_button("⬅️ Previous step")
        self.assertEqual(self.last_bot_message, "What is your favourite sport?")
        self.click_on_button("🤺 Fencing")
        self.assertEqual(self.last_bot_message, "Would you like to submit Fencing as your favourite sport?")
        self.click_on_button("✅ Yes")
        self.assertEqual(self.last_bot_message, "Thank you! Your favourite sport Fencing has been recorded.")

    def test_echo_command(self):
        """Test the echo command."""
        self.send_text("/echo")
        self.assertEqual(self.last_bot_message, "Send the message you want to echo:")
        self.send_text("Hello, World!")
        self.assertEqual(self.last_bot_message, "You said: Hello, World!")

    def test_unknown_command(self):
        """Test sending an unknown command."""
        self.send_text("/unknowncommand")
        self.assertIn("Currently available commands", self.last_bot_message)

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
                self.webhook_url,
                data={},
                headers={"X-Telegram-Bot-Api-Secret-Token": "any_token"},
                content_type="application/json",
            )
        self.assertEqual(response.status_code, 200)

    def test_call_command_step_do_nothing(self):
        """Test that calling a command step with token DO_NOTHING it does nothing."""
        called = _call_command_step(DO_NOTHING, MagicMock(), MagicMock())
        self.assertFalse(called)

    def test_call_command_step_callback_not_found(self):
        """Test that calling a command step with an invalid token raises."""
        uuid_token = str(uuid.uuid4())
        CallbackData.objects.filter(token=uuid_token).delete()  # Ensure it does not exist
        called = _call_command_step(uuid_token, MagicMock(), MagicMock())
        self.assertFalse(called)

    def test_command_has_steps_abstract(self):
        """Test that accessing steps property on BaseBotCommand raises NotImplementedError."""
        command = BaseBotCommand(MagicMock())
        with self.assertRaises(NotImplementedError):
            _ = command.steps

    def test_step_handle_abstract(self):
        """Test that calling handle method on Step raises NotImplementedError."""
        step = Step(MagicMock())
        with self.assertRaises(NotImplementedError):
            step.handle(MagicMock())

    def test_steps_back_does_nothing_when_idx_out_of_bounds(self):
        """Test that steps_back does nothing when index would go out of bounds."""

        class DummyCommand(BaseBotCommand):
            @property
            def steps(self):
                return [Step(self, unique_id="step_1"), Step(self, unique_id="step_2")]

        telegram_settings = MagicMock(name="telegram_settings")
        telegram_update = MagicMock(name="telegram_update")

        command = DummyCommand(telegram_settings)
        with patch.object(command, "get_callback_data", return_value={"_steps_back": 1}):
            command.previous_step("step_1", telegram_update)  # Go back from first step, this should just do nothing

    def test_step_get_callback_data_calls_command_get_callback_data_if_not_waiting_for_input(self):
        """Test that Step.get_callback_data calls Command.get_callback_data if not waiting for input."""

        class DummyCommand(BaseBotCommand):
            @property
            def steps(self):
                return [Step(self, unique_id="step_1"), Step(self, unique_id="step_2")]

        telegram_settings = MagicMock(name="telegram_settings")
        telegram_update = MagicMock(name="telegram_update")
        telegram_update.callback_data = ""
        telegram_update.is_message.return_value = True
        telegram_update.is_command.return_value = False
        telegram_settings.data = {}
        command = DummyCommand(telegram_settings)
        with patch.object(command, "get_callback_data") as fake_get_callback_data:
            command.steps[0].get_callback_data(telegram_update)
            fake_get_callback_data.assert_called_once_with(telegram_update.callback_data)

    def test_get_or_create_telegram_settings_creates_if_allowed(self):
        """Test that get_or_create_telegram_settings creates settings if allowed."""
        telegram_update = SimpleNamespace(chat_id=987654321)
        with patch.object(settings, "ALLOW_SETTINGS_CREATION_FROM_UPDATES", False):
            with self.assertRaises(get_telegram_settings_model().DoesNotExist):
                _get_or_create_telegram_settings(telegram_update)  # type: ignore[reportArgumentType]

        with patch.object(settings, "ALLOW_SETTINGS_CREATION_FROM_UPDATES", True):
            telegram_settings = _get_or_create_telegram_settings(telegram_update)  # type: ignore[reportArgumentType]
            self.assertIsNotNone(telegram_settings)
            self.assertEqual(telegram_settings.chat_id, 987654321)

    def test_create_callback_provides_default(self):
        """Test that create_callback provides a default value if no kwargs are provided."""
        telegram_settings = MagicMock(name="telegram_settings")
        command = BaseBotCommand(telegram_settings)
        callback_token = command.create_callback("dummy_step", "next_step")
        callback_data = command.get_callback(callback_token)
        self.assertIn("correlation_key", callback_data.data)

    def test_step_create_callback_always_includes_correlation_key(self):
        """Test that Step.*_step_callback provides includes a correlation key if no or bad original data is provided."""
        telegram_settings = MagicMock(name="telegram_settings")
        command = BaseBotCommand(telegram_settings)
        step = Step(command)
        callback_token = step.next_step_callback(some_value=123)
        callback_data = command.get_callback(callback_token)
        self.assertIn("correlation_key", callback_data.data)

        callback_token = step.previous_step_callback(1, some_value=123)
        callback_data = command.get_callback(callback_token)
        self.assertIn("correlation_key", callback_data.data)

        callback_token = step.current_step_callback(some_value=123)
        callback_data = command.get_callback(callback_token)
        self.assertIn("correlation_key", callback_data.data)

        callback_token = step.cancel_callback(some_value=123)
        callback_data = command.get_callback(callback_token)
        self.assertIn("correlation_key", callback_data.data)

        callback_token = step.next_step_callback(original_data={"faulty": "original"}, some_value=123)
        callback_data = command.get_callback(callback_token)
        self.assertIn("correlation_key", callback_data.data)

    def test_click_on_text_deprecation(self):
        """Test that click_on_text raises a deprecation warning."""
        with self.assertWarns(DeprecationWarning) as cm:
            with patch.object(self, "click_on_button", return_value=MagicMock()):
                self.click_on_text("Some Text")
        self.assertIn("click_on_text is deprecated", str(cm.warning))

    def test_click_on_button_by_index_invalid_type(self):
        """Test that click_on_button raises ValueError when given an invalid type."""
        with self.assertRaises(ValueError) as cm:
            with patch.object(self.fake_bot_post, "call_args", new=MagicMock()):
                self.click_on_button(3.14)  # Invalid type: float  # type: ignore[reportArgumentType]
        self.assertIn("button must be a string or an integer index", str(cm.exception))

    def test_bot_send_help_custom_renderer(self):
        """Test that bot.send_help uses a custom help renderer if configured."""

        def custom_help_renderer(telegram_settings):  # noqa: ARG001  # pylint: disable=unused-argument
            return "Custom Help Text"

        telegram_settings = MagicMock(name="telegram_settings")
        telegram_update = SimpleNamespace(chat_id=123456789, language_code=None)
        with patch.object(settings, "HELP_RENDERER", "path.to.custom_help_renderer"):
            with patch("django_telegram_app.bot.bot.import_string", return_value=custom_help_renderer):
                send_help(telegram_update, telegram_settings)  # type: ignore[reportArgumentType]

        self.assertEqual(self.last_bot_message, "Custom Help Text")


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
