# 🧩 Bot Architecture

This guide explains the core building blocks of **django-telegram-app** and how they work together.

## Core Components

### 1. Telegram Webhook View
All Telegram updates are sent to Django through a webhook endpoint.  
This is automatically wired using:

```python
path(telegram_app_settings.ROOT_URL, include("django_telegram_app.urls"))
```

The webhook view:
- validates the secret token
- normalizes the raw Telegram payload into a `TelegramUpdate`
- hands the update to the dispatcher

---

### 2. Dispatcher
The dispatcher determines whether the update:
- starts a new command
- continues an existing command
- triggers a callback
- send the help message
- or should be ignored

The dispatcher instantiates the appropriate `BaseBotCommand` subclass based on the incoming update.

---

### 3. Commands and Steps
A command defines a multi-step interaction.  
Each step is a subclass of `Step` and implements a `handle()` method.

Commands define their flow via:

```python
@property
def steps(self):
    return [StepOne(self), StepTwo(self)]
```

The dispatcher calls the correct step based on stored callback data.

---

### 4. CallbackData Model
Callback data is stored in the database rather than embedding long strings in Telegram callback buttons.
This bypasses Telegram's size limits and allows flexible state passing.

---

### 5. TelegramSettings
Represents the chat/user context and persists per-user bot state.

---

Together these components allow building robust, testable, multi-step conversational flows.
