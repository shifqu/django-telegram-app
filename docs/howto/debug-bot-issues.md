# 🐞 How to Debug Bot Issues

Debugging Telegram bot behavior can sometimes be tricky, especially when dealing with webhooks, callback data, or complex multi-step commands.
This guide offers a practical checklist and techniques for diagnosing and fixing issues in **django-telegram-app**.

---

## 1. Verify incoming updates

If your bot does not respond, first confirm that Telegram updates are actually reaching your server.

### Check message logs in the admin

Visit:

```
/admin/django_telegram_app/message/
```

If messages appear here:

- Your webhook is configured correctly.
- Django is receiving the update.

If **no messages** appear, see the webhook troubleshooting section below.

---

## 2. Check webhook configuration

Telegram requires:

- A **valid HTTPS** endpoint
- A valid **secret token header**
- A fully reachable domain (no firewalls blocking POST requests)

If needed, reset the webhook:

```
python manage.py setwebhook <base-url>
```

During local development, use tunnels such as **localhost.run**, **Pinggy**, or **ngrok**.

---

## 3. Inspect raw update payloads

If parsing or step routing behaves unexpectedly, log or inspect the raw request:

### Temporary debugging helper

Inside a command or step:

```python
print("DEBUG UPDATE:", telegram_update.__dict__)
```

or for entire JSON:

```python
import json
print(json.dumps(update, indent=2))
```

You can also use Django’s `logging` module for structured output.

---

## 4. Debug callback issues

Callback problems usually fall into one of these categories:

### 1. Missing or expired callback data
If the correlation key was cleared after a command finished, buttons referencing old tokens will fail.

### 2. Incorrect callback token in keyboard
Double-check:

```python
keyboard = [
    {"callback_data": self.next_step_callback(...)}
]
```

If you accidentally pass the wrong data or mutated kwargs, the callback will not load correctly.

### 3. Overwriting your stored callback data
Calling `data.pop("key")` or modifying `data` without re-passing it into callback helpers may lose state.

---

## 5. Debug waiting-for-input issues

If the bot is ignoring a text message:

- Ensure the previous step called:

```python
self.add_waiting_for("field_name", data)
```

- Confirm `"field_name"` exists in callback data at the next step
- Make sure the message was **not** interpreted as a command (`/something`)
- Check that your `TelegramSettings.data` is not being overwritten elsewhere

Use the admin to inspect the stored field in:

```
/admin/django_telegram_app/telegramsettings/
```

---

## 6. Use tests to reproduce bugs

Create a failing test with `TelegramBotTestCase`:

```python
self.send_text("/roll")
self.click_on_button("🎲 d20")
self.assertIn("You rolled", self.last_bot_message)
```

Tests allow you to step through the exact scenario you want to debug, without relying on Telegram or tunnels.

---

## 7. Check for configuration issues

Run:

```
python manage.py check
```

Common problems include:

- Missing `BOT_URL`
- Misconfigured webhook URL parts
- Missing custom TelegramSettings after swapping

Fix any warnings or errors shown.

---

## 8. Confirm your domain and HTTPS

Telegram will **not** deliver updates to:

- HTTP-only URLs
- expired certificates
- self-signed certificates
- Cloudflare proxies blocking POST requests
- ports other than 443 (unless manually allowed)

Use:

```
curl -I https://your-domain.com
```

Look for 200/301 responses.

---

## 9. Examine server logs

Your Django logs may show:

- JSON parsing errors
- callback lookup failures
- step index errors
- missing fields

If you're running via Docker:

```
docker compose logs -f
```

Logs often expose the root cause immediately.

---

## 10. Clear stale state during debugging

You may have old or broken state stored in your `TelegramSettings.data`.

Reset it:

```python
from django_telegram_app.models import TelegramSettings
s = TelegramSettings.objects.get(chat_id=...)
s.data = {}
s.save()
```

---

## 🧭 Summary

When debugging:

1. Confirm updates reach your server
2. Inspect messages in the admin
3. Verify the webhook
4. Print or log raw updates
5. Ensure callback data is correct
6. Use tests to reproduce issues
7. Clear stale per-chat state

With these tools, you can diagnose nearly any bot issue in minutes.
