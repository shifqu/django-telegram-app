"""Reusable testcases for Telegram bot app."""

import warnings
from unittest.mock import MagicMock, patch

from django.test.testcases import TestCase
from django.urls import reverse

from django_telegram_app.conf import settings


class TelegramBotTestCase(TestCase):
    """Base test case for Telegram bot tests."""

    @property
    def webhook_url(self):
        """Return the webhook URL."""
        return reverse("webhook")

    @classmethod
    def tearDownClass(cls):
        """Tear down class-level patches."""
        try:
            super().tearDownClass()
        finally:
            patch.stopall()

    def setUp(self):
        """Set up each test."""
        self.fake_bot_post = patch("django_telegram_app.bot.bot.post", MagicMock()).start()

    def click_on_text(self, text: str, verify: bool = True):
        """Simulate a click on the specified text button."""
        warnings.warn(
            "click_on_text is deprecated and will be removed in version 2. Use click_on_button instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.click_on_button(text, verify=verify)

    def click_on_button(self, button: str | int, verify: bool = True):
        """Simulate a click on an inline button by text or index.

        When `button` is a string, it searches for a button with matching text.
        When `button` is an integer, it treats it as the index of the button in
        the inline keyboard (flattened).
        """
        inline_keyboard = self.fake_bot_post.call_args[1]["payload"]["reply_markup"]["inline_keyboard"]
        if isinstance(button, str):
            callback_data = [item for row in inline_keyboard for item in row if item["text"] == button][0][
                "callback_data"
            ]
        elif isinstance(button, int):
            flat_buttons = [item for row in inline_keyboard for item in row]
            callback_data = flat_buttons[button]["callback_data"]
        else:
            raise ValueError("button must be a string or an integer index")

        data = self.construct_telegram_callback_query(callback_data)
        response = self.post_data(data, verify=verify)
        return response

    def send_text(self, text: str, verify: bool = True):
        """Simulate sending a text message."""
        payload = self.construct_telegram_update(text)
        return self.post_data(payload, verify=verify)

    def post_data(self, data: dict, verify: bool = True):
        """Post data to the webhook."""
        response = self.client.post(
            self.webhook_url,
            data=data,
            headers={"X-Telegram-Bot-Api-Secret-Token": settings.WEBHOOK_TOKEN},
            content_type="application/json",
        )
        if verify:
            self.assertEqual(response.json(), {"status": "ok", "message": "Message received."})
        return response

    @property
    def last_bot_message(self) -> str:
        """Return the last message sent by the bot.

        This is a convenience property for tests and can be used to verify the last message.

        Example:
            self.send_text("/start")
            self.assertEqual(self.last_bot_message, "Welcome to the bot!")
        """
        return self.fake_bot_post.call_args[1]["payload"]["text"]

    @staticmethod
    def construct_telegram_update(message_text: str):
        """Construct a minimal telegram update."""
        return {"message": {"chat": {"id": 123456789}, "text": message_text}}

    @staticmethod
    def construct_telegram_callback_query(callback_data: str):
        """Construct a minimal telegram callback query."""
        return {
            "callback_query": {
                "message": {"message_id": 123, "chat": {"id": 123456789, "first_name": "test", "type": "private"}},
                "data": callback_data,
                "from": {"id": 123456789, "is_bot": False, "first_name": "test"},
            }
        }
