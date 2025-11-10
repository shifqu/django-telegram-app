"""Testing utilities for Telegram bot app."""

from unittest.mock import MagicMock, patch

from django.test.testcases import TestCase
from django.urls import reverse

from django_telegram_app.conf import settings


class TelegramBotTestCase(TestCase):
    """Base test case for Telegram bot tests."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data for the testcase."""
        cls.url = reverse("webhook")

    def setUp(self):
        """Set up each test."""
        self.fake_bot_post = patch("apps.telegram.bot.bot.post", MagicMock()).start()

    def click_on_text(self, text: str):
        """Simulate a click on the specified text button."""
        inline_keyboard = self.fake_bot_post.call_args[1]["payload"]["reply_markup"]["inline_keyboard"]
        callback_data = [item for row in inline_keyboard for item in row if item["text"] == text][0]["callback_data"]
        data = self.construct_telegram_callback_query(callback_data)
        response = self.post_data(data)
        return response

    def send_text(self, text: str, verify: bool = True):
        """Simulate sending a text message."""
        payload = self.construct_telegram_update(text)
        return self.post_data(payload, verify=verify)

    def post_data(self, data: dict, verify: bool = True):
        """Post data to the webhook."""
        response = self.client.post(
            self.url,
            data=data,
            headers={"X-Telegram-Bot-Api-Secret-Token": settings.WEBHOOK_TOKEN},
            content_type="application/json",
        )
        if verify:
            self.assertEqual(response.json(), {"status": "ok", "message": "Message received."})
        return response

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
            }
        }
