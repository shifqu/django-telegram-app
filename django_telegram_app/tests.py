"""Telegram tests."""

from django.contrib.auth import get_user_model

from django_telegram_app.bot.testing import TelegramBotTestCase
from django_telegram_app.resolver import get_telegram_settings_model


class TelegramTestCase(TelegramBotTestCase):
    """Telegram test case."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        super().setUpTestData()
        cls.user = get_user_model().objects.create_user(username="dummyuser", password="dummypass")
        cls.telegram_setting = get_telegram_settings_model().objects.create(user=cls.user, chat_id=123456789)

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
        """Test the telegram send help command."""
        self.send_text("dummy text")
        self.assertEqual(self.fake_bot_post.call_count, 1)
        self.assertEqual(self.fake_bot_post.call_args.args[0], "sendMessage")
        self.assertIn("Currently available commands", self.fake_bot_post.call_args[1]["payload"]["text"])
