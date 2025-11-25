# 🧪 Testing

Testing Telegram bot commands in **django-telegram-app** is designed to be simple, fast, and deterministic.

This guide explains the testing tools provided by the framework and how to use them effectively.

---

## Goals of the Testing Framework

The built‑in test utilities help you:

- simulate incoming Telegram messages and callback queries
- assert that your bot responded with specific messages
- test multi‑step commands (including callback flows)
- inspect the last message your bot sent
- avoid real API calls by automatically mocking the Telegram client

These tools ensure your bot's logic can be tested fully **without network access**.

---

## TelegramBotTestCase

All tests should subclass:

```python
from django_telegram_app.testing import TelegramBotTestCase
```

This base class provides:

- `send_text(message)` – simulate an incoming text message  
- `click_on_text(button_label)` – simulate clicking an inline keyboard button  
- `last_bot_message` – inspect the most recent bot message  
- automatic mocking of `bot.post(...)`  
- a helper method for posting raw update payloads  

---

## Example: Testing a simple command

Assume the `/roll` command returns “Choose a die to roll:”.

```python
class RollCommandTests(TelegramBotTestCase):
    def test_start_roll_command(self):
        self.send_text("/roll")
        self.assertIn("Choose a die", self.last_bot_message)
```

---

## Testing callback flows

To simulate pressing an inline button:

```python
self.send_text("/roll")
self.click_on_text("🎲 d6")
self.assertIn("You rolled", self.last_bot_message)
```

`click_on_text()` automatically:

1. inspects the last keyboard sent by the bot  
2. finds the correct button by text  
3. constructs a callback query update  
4. posts it to the webhook  

---

## Testing “waiting for input”

When a step uses:

```python
self.add_waiting_for("character_name", data)
```

the next non‑command message will be stored in the callback data.

Example:

```python
def test_character_name_flow(self):
    self.send_text("/roll")            # triggers AskCharacterName
    self.send_text("Gimli")            # stored under "character_name"
    self.click_on_text("🎲 d20")       # choose die
    self.assertIn("Gimli rolled", self.last_bot_message)
```

---

## Inspecting all messages

```python
messages = [
    call.kwargs["payload"]["text"]
    for call in self.fake_bot_post.call_args_list
]
```

---

## Cleanup

`TelegramBotTestCase` ensures:

- all mocks are cleaned up  
- callback data created during tests is removed  
- webhook posting uses your project's `WEBHOOK_TOKEN`  

---

## Summary

The testing tools in **django-telegram-app** let you:

- write clear, readable tests  
- exercise full multi‑step command flows  
- avoid network calls  
- assert bot output precisely  

Testing your bot becomes as simple as testing any other Django component.
