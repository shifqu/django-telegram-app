# 🔄 Update Flow

This guide walks through the full lifecycle of a Telegram update.

---

## 1. Telegram → Webhook
Telegram sends a POST request with JSON payload to your webhook URL.

---

## 2. WebhookView validation
The built‑in webhook view:
- checks the secret token header
- parses JSON
- wraps it in a `TelegramUpdate`

---

## 3. Dispatcher Routing
The dispatcher inspects the update:

- If it's a **message** and starts with `/command`, it starts a new command.
- If it's a **callback query**, it resumes an existing command using callback data.
- If it's a **message** that is *not* a command but the user is in a "waiting_for" state,  
  it passes the message to the correct step.

---

## 4. Command execution
The dispatcher instantiates the command class:

```python
cmd = MyCommand(settings)
```

Then it calls the appropriate step:

```python
cmd.start(update)
```

or later:

```python
getattr(command, data.action)(data.step, telegram_update)
```

---

## 5. Bot Response
Steps call:

```python
bot.send_message(...)
```

which sends the appropriate Telegram API request.

---

## 6. Cleanup
When a command finishes, the framework clears any associated callback data using the correlation key.

---

This predictable flow makes commands deterministic and easy to test.
