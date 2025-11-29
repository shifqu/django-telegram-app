# 🎲 Writing Tests For Your First Command

This tutorial starts where [extend dice roller](dice-roller-tutorial-ext.md) left off. You’ll write unit-tests for the **D&D-style dice roller** by using the provided `TelegramBotTestCase`.

By the end, you will:

- know how to test your bot with provided utilities
- have a fully tested bot

This assumes you already:

- implemented and extended the `/roll` command
- have basic knowledge on [testing django apps](https://docs.djangoproject.com/en/5.2/topics/testing/){: target="_blank"}

---

## 1. Create the RollCommandTests class

Add the following to `dice/tests.py`:

```python title="dice/tests.py"
"""Tests for the roll command."""

from django_telegram_app import get_telegram_settings_model
from django_telegram_app.bot.testing.testcases import TelegramBotTestCase


class RollCommandTests(TelegramBotTestCase):
    """Tests for the /roll command."""

    @classmethod
    def setUpTestData(cls):
        """Set up the test data by creating a TelegramSettings entry."""
        cls.telegramsettings = get_telegram_settings_model().objects.create(chat_id="123456789")

    def test_roll_command_flow(self):
        """Test the full flow of the /roll command."""
        self.send_text("/roll")
        self.assertEqual(self.last_bot_message, "What's your character's name?")
        self.send_text("Gandalf")
        self.assertEqual(self.last_bot_message, "Choose a die to roll:")
        self.click_on_button("🎲 d20")
        self.assertRegex(self.last_bot_message, "Gandalf rolled .* on a d20! 🎉")
        self.click_on_button("🔁 Roll again")
        self.assertRegex(self.last_bot_message, "Gandalf rolled .* on a d20! 🎉")
        self.click_on_button("🎯 Choose another die")
        self.assertEqual(self.last_bot_message, "Choose a die to roll:")
        self.click_on_button("🎲 d8")
        self.assertRegex(self.last_bot_message, "Gandalf rolled .* on a d8! 🎉")
        self.click_on_button("✏️ Choose another name")
        self.assertEqual(self.last_bot_message, "What's your character's name?")
        self.send_text("Gimli")
        self.assertEqual(self.last_bot_message, "Choose a die to roll:")
        self.click_on_button("🎲 d4")
        self.assertRegex(self.last_bot_message, "Gimli rolled .* on a d4! 🎉")

```

---

## 2. Understanding the `RollCommandTests` class
As you could already see, the testing class is quite standard Django.
The `TelegramBotTestCase` comes with some helper functions and properties.
- send_text: Effectively send a text to the bot
- click_on_button: Simulate a button click to the bot
- last_bot_message: Property that returns the text of last message the bot sent

!!! note
    For more information on the TelegramBotTestCase, see [testing](../topics/testing.md) or the [technical reference](../reference/api/bot/testcases.md)

---

## Next steps

Continue to:

**[👉 What to read next](whats-next.md)**