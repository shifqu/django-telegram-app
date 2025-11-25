# 🛠 TelegramSettings Design

`TelegramSettings` represents the per-chat configuration and runtime context.

Projects may provide their own concrete implementation via:

```python
TELEGRAM_SETTINGS_MODEL = "myapp.CustomTelegramSettings"
```

---

## Core Responsibilities

### 1. Identify the chat
`chat_id` is the primary identifier for routing messages.

### 2. Persist user preferences
Examples:
- language
- notification settings
- custom preferences for your bot

### 3. Store ephemeral command state
The `data` JSONField is used for:
- `_waiting_for` markers
- free-form extra state used by commands

### 4. Determine command ownership
Each command instance receives settings:

```python
Command(settings=TelegramSettings)
```

providing the context needed for the interaction.

---

## Why is user linking optional?

Some bots use Telegram as authentication for an existing user model.  
Others allow anonymous Telegram-based interactions.

By keeping the user field optional and swappable:
- simple bots don’t need a user model
- complex bots can integrate tightly with Django’s auth system

---

## Admin integration

If `REGISTER_DEFAULT_ADMIN = True`, the library registers a useful model admin for TelegramSettings.

Projects may override or disable this depending on needs.

---

`TelegramSettings` is the central anchor point connecting Telegram chats to Django models, state, and command execution.
