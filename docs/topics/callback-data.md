# 🎛 Callback Data

**Callback data** powers multi-step interactions in `django-telegram-app`.

Instead of storing JSON or long strings in Telegram callback buttons,
the library stores structured data in the `CallbackData` model and inserts a short token into the button.

## Why this approach?

- Telegram limits callback data to 64 bytes  
- Many commands need to pass structured data (ids, choices, state markers)
- Storing in DB avoids encoding/decoding issues
- Database entries are automatically cleaned up when a command finishes

---

## Creating callback data

Inside a step:

```python
token = self.next_step_callback(some_value=123)
```

This:
1. Creates a default `CallbackData` object
2. Stores your provided kwargs
3. Returns a short token string to use in the inline button

---

## Retrieving callback data

When a user taps a button:

```python
data = self.get_callback_data(update)
```

This:
- resolves the token
- returns the stored dict

---

## Default Callback Data

If a step is triggered without callback data (e.g. first step),  
the framework injects:

```python
{"correlation_key": "<uuid>"}
```

The correlation key links all callback data for the same command execution.

---

Callback data is central to building multi-step flows with correct context and minimal payload size.
