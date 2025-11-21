# 🧪 Testing

## TL;DR

To test your bot:

1. Subclass `TelegramBotTestCase`.
2. Use `send_text("/command")` to simulate user messages.
3. Use `click_on_text("Button")` for inline buttons.
4. Use `verify_message_log([...])` to assert outgoing messages.
5. Use `post_data(...)` + `verify=False` for custom payloads.

This gives you reliable, high-level bot tests without needing to mock the entire update flow manually.

---

## What & Why
**django-telegram-app** provides a reusable test case class to make it easy to
test your Telegram bot commands end-to-end, using Django’s test client and a
mocked Telegram bot.

Import it like this:
```python
from django_telegram_app.testing.testcases import TelegramBotTestCase
```

By subclassing `TelegramBotTestCase`, you can:

- send messages to your webhook as if they came from Telegram
- simulate inline button clicks (callback queries)
- assert which messages your bot sends
- avoid real network calls (Telegram API is fully mocked)

---

## What TelegramBotTestCase provides

`TelegramBotTestCase` extends `django.test.TestCase` and adds:

- automatic patching of `django_telegram_app.bot.bot.post` (so no real HTTP)
- a `webhook_url` property resolving your webhook endpoint
- helpers for posting Telegram-style payloads
- convenience methods:
```python
send_text(message)
click_on_text(button_label)
verify_message_log(expected_messages)
```

It also provides two static helpers for building minimal Telegram update payloads:
```python
construct_telegram_update(text)
construct_telegram_callback_query(callback_data)
```

You normally will not need these directly.

---

## Testing a command

```python title="Testing that '/start' replies with 'Welcome!'"
from django_telegram_app.testing.testcases import TelegramBotTestCase

class StartCommandTests(TelegramBotTestCase):
    def test_start_sends_welcome(self):
        self.send_text("/start")
        self.verify_message_log(["Welcome!"])
```
Explanation:

- `send_text("/start")` posts a minimal update to the webhook
- `verify_message_log([...])` checks the bot’s outgoing messages

---

## Testing inline buttons

If your bot sends inline keyboard buttons, you can test button clicks using
`click_on_text`.

```python
class ButtonTests(TelegramBotTestCase):
    def test_click_yes_button(self):
        self.send_text("/ask")
        self.click_on_text("Yes")
        self.verify_message_log([
            "Choose an option:",
            "You chose Yes!",
        ])
```
How it works:

- Reads the inline keyboard from the bot’s last response
- Finds the button with matching text
- Extracts its callback data
- Sends a callback query update to the webhook

---

## Controlling response verification

By default, all helper methods verify that the webhook responds with:
```python
{"status": "ok", "message": "Message received."}
```

To disable this assertion:
```python
response = self.send_text("/start", verify=False)
self.assertEqual(response.status_code, 200)
```

Same for button clicks:
```python
self.click_on_text("Yes", verify=False)
```

---

## Custom update payloads

For advanced scenarios, you can bypass the helpers:
```python
class CustomPayloadTests(TelegramBotTestCase):
    def test_custom_payload(self):
        payload = {
            "message": {
                "chat": {"id": 999},
                "text": "/special",
            }
        }
        response = self.post_data(payload)
        self.assertEqual(response.status_code, 200)
```

Use `verify=False` if you want to control the expected JSON:
```python
self.post_data(payload, verify=False)
```

---

## Webhook authentication

The helper sends the correct header automatically:
```text
X-Telegram-Bot-Api-Secret-Token: <settings.WEBHOOK_TOKEN>
```

It reads the token from:
```python
TELEGRAM["WEBHOOK_TOKEN"]
```

If your webhook requires this token, make sure it is set or patched in tests.

---

## Patching details

`TelegramBotTestCase` automatically:

- patches `django_telegram_app.bot.bot.post` in `setUp`
- stores it as `self.fake_bot_post`
- stops all patches in `tearDownClass`

You may inspect outgoing messages manually:
```python
call = self.fake_bot_post.call_args_list[0]
payload = call.kwargs["payload"]
self.assertIn("Welcome", payload["text"])
```
