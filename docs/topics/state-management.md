# 🧠 State Management

State is managed at two levels:

---

## 1. Command Step State (CallbackData)
Short‑term state tied to a single execution of a command.

- Stored in the `CallbackData` model
- Automatically cleaned up when the command finishes
- Used for structured per‑step metadata (like choices, flags, user answers)

---

## 2. Persistent User State (TelegramSettings.data)
Per-chat data stored on the TelegramSettings model:

```python
self.add_waiting_for("username", data)
```

The framework will add the waiting_for on `TelegramSettings.data`
```python
settings.data = {"_waiting_for": "..."}
settings.save()
```

This is currently used for a single feature:
- waiting for free‑text input

---

## Waiting for Input

Steps may request text input:

```python
self.add_waiting_for("character_name")
```

The next non-command message updates the callback data under `"character_name"`.

---

## Clearing State

Commands automatically clear:
- `settings.data`
- all callback data with the same correlation key

You can manually clear or update state in advanced scenarios.

---

Combining callback data with `TelegramSettings.data` gives a flexible and safe state model
for multi-step interactions.
