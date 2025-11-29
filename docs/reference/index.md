# 📘 API Reference

The reference section provides a **technical, low-level view** of the core pieces of
**django-telegram-app** – classes, models, configuration, and checks.

Unlike tutorials (which show you *how* to build something) and topic guides
(which explain *why* things are designed the way they are), this section answers:

> “What attributes and methods does this class have, and how do I use them correctly?”

You’ll typically come here when you already know which component you want to use
(e.g. `Step`, `TelegramSettings`, `CallbackData`) and need the details.

---

## Bot API

These pages cover the **core building blocks** you use to implement and test commands.

- **[BaseBotCommand](api/bot/base-bot-command.md)**  
  The base class for all bot commands.  
  Describes how commands are constructed, how the `steps` sequence works, and how
  to start, finish, cancel, and navigate between steps.

- **[Step](api/bot/step.md)**  
  The building block of multi-step conversations.  
  Documents the `handle()` method, callback helpers (`next_step_callback`, `previous_step_callback`, etc.),
  and utilities like `get_callback_data()` and `add_waiting_for()`.

- **[TelegramUpdate](api/bot/telegram-update.md)**  
  A normalized wrapper around Telegram’s raw update payload.  
  Explains how messages and callback queries are represented and how to inspect
  chat IDs, message text, callback data, and type helpers like `is_message()`.

- **[TestCases](api/bot/testcases.md)**  
  Reference for the testing helpers (e.g. `TelegramBotTestCase`).  
  Covers methods such as `send_text()`, `click_on_button()`, `last_bot_message`,
  and how the bot client is mocked in tests.

---

## Core Models

These models underpin the persistence and routing of Telegram-related data.

- **[CallbackData](api/callbackdata.md)**  
  Stores structured callback payloads for inline buttons.  
  Documents the data structure, token field, correlation key, and lifecycle.

- **[Message](api/message.md)**  
  Represents incoming and outgoing messages for logging and debugging.  
  Details the fields used to trace bot interactions.

- **[TelegramSettings](api/telegramsettings.md)**  
  The per-chat configuration and state model.  
  Explains required fields, the `data` JSON field, and how to swap in your own
  implementation via `TELEGRAM_SETTINGS_MODEL`.

---

## System Checks

- **[Checks](checks.md)**  
  Describes the Django system checks registered by `django-telegram-app`.  
  Use this reference to understand what each check validates, what the messages mean,
  and how to resolve configuration or integration issues highlighted by `manage.py check`.

---

## Configuration

- **[Configuration](configuration.md)**  
  A complete reference of all settings used by **django-telegram-app**.  
  Includes required and optional settings, defaults, and how they interact
  (e.g. webhook URL parts, swappable models, admin registration flags).

---

## How to use this section

- If you’re **implementing a new command**, start with:
  - [BaseBotCommand](api/bot/base-bot-command.md)
  - [Step](api/bot/step.md)
  - [TelegramUpdate](api/bot/telegram-update.md)

- If you’re **debugging callbacks or state**, refer to:
  - [CallbackData](api/callbackdata.md)
  - [TelegramSettings](api/telegramsettings.md)

- If you’re **configuring or integrating into a larger project**, check:
  - [Configuration](configuration.md)
  - [Checks](checks.md)

The reference is meant to be **lookup-friendly**: jump in, find the class or setting
you care about, and get back to building your bot.
