"""Tests for the models package."""

from django.test import TestCase

from django_telegram_app.models import CallbackData, Message, TelegramSettings


class ModelsTests(TestCase):
    """Tests for the models package."""

    def test_message_message_truncated(self):
        """Test that the message_truncated property works as expected."""
        msg = Message(raw_message="a" * 500)
        self.assertEqual(len(msg.message_truncated), 100)
        self.assertEqual(msg.message_truncated[-3:], "...")

        msg_short = Message(raw_message="Short message")
        self.assertEqual(msg_short.message_truncated, "Short message")

    def test_message_update_id(self):
        """Test that the update_id property works as expected."""
        msg = Message(raw_message={"update_id": 12345})
        self.assertEqual(msg.update_id, 12345)

        msg_no_id = Message(raw_message={})
        self.assertEqual(msg_no_id.update_id, "unknown")

    def test_message_str(self):
        """Test that the __str__ method of Message works as expected."""
        msg = Message(raw_message={"update_id": 12345})
        self.assertEqual(str(msg), "12345")

        msg_with_error = Message(raw_message={"update_id": 67890}, error="Some error")
        self.assertEqual(str(msg_with_error), "67890 - Some error")

    def test_telegram_settings_str(self):
        """Test that the __str__ method of TelegramSettings works as expected."""
        settings = TelegramSettings(chat_id="67890")
        self.assertEqual(str(settings), "Chat 67890")

    def test_callback_data_str(self):
        """Test that the __str__ method of CallbackData works as expected."""
        uuid_token = "9e265e02-6b4c-41f8-8edd-c12e8e601469"
        data = {"key": "value"}
        callback = CallbackData(token=uuid_token, command="/test", step="step1", action="cancel", data=data)
        self.assertEqual(str(callback), f"{uuid_token} - {data}")

    def test_callback_data_data_truncated(self):
        """Test that the data_truncated property of CallbackData works as expected."""
        data = {"a" * 111: "value"}
        callback = CallbackData(command="/test", step="step1", action="cancel", data=data)
        self.assertEqual(len(callback.data_truncated), 100)
        self.assertEqual(callback.data_truncated[-3:], "...")
