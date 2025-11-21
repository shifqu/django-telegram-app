# 🤖 Writing Bot Commands

Bot commands in **django-telegram-app** provide a structured, multi-step conversational flow.
Each command module contains:

- a `Command` class (subclass of `BaseCommand`)
- one or more `Step` subclasses

Commands are automatically discovered from every installed Django app.

---

## Command Discovery
Each Django app may define telegram bot commands under:

```text title="Example file tree"
myapp/
    __init__.py
    telegrambot/
        __init__.py
        commands/
            __init__.py
            _private.py
            roll.py
```

Rules:
- Files in `telegrambot/commands/` are imported automatically.
- Modules beginning with `_` are **ignored**.
- Each public module must define a `Command` class.

If `myapp` is in `INSTALLED_APPS`, commands are available to the bot.

!!! note
    This is exactly how django handles [management commands](https://docs.djangoproject.com/en/5.2/howto/custom-management-commands/){: target="_blank"}

---

## Command Structure

A command:

- Receives a `TelegramSettings` instance  
- Has one or more steps  
- Starts at the first step  
- Moves forward/backward based on callback actions  
- Stores temporary state in `CallbackData`'s `.data` JSON field

---

## How Commands Work

Here is a conceptual flow of a command
```text
User sends "/roll"
framework loads command
first step runs
step sends a message with buttons or asks for input
user clicks a button or responds with text
framework calls the command step from the callbackdata
etc
```

The framework handles:

- callback storage
- step navigation
- clearing state
- parsing Telegram updates

You only implement steps.

---

## Steps

A command defines its steps:
```python
@property
def steps(self):
    return [AskName(self), ConfirmName(self)]
```
Each step implements:
```python
def handle(self, telegram_update):
    ...
```

A step may:

- get callback data
- collect user input
- create inline keyboards
- send messages
- navigate steps
- create callback data (eg.: to store collected answers)

---

## 🧩 Callback Data

When you create a button:
```python
{"text": "Yes", "callback_data": self.next_step_callback(answer=True)}
```

The framework:

- creates a CallbackData record
- stores your kwargs
- generates a token
- sends only the token to Telegram
- resolves token automatically later

---

## User Input

Use user input instead of buttons:
```python
self.add_waiting_for("username", data)
```

When the user sends text:

- framework fetches `waiting_for` token
- stores text under `data["username"]`
- passes it to the next step automatically

---

## Example: Multi-Step Command

from django_telegram_app import bot
from django_telegram_app.base import BaseCommand, Step, TelegramUpdate

class Command(BaseCommand):
    description = "Register a user by asking for name and confirmation."

    @property
    def steps(self):
        return [AskName(self), ConfirmName(self), RegistrationDone(self)]

### Step 1 — ask name

class AskName(Step):
    def handle(self, update):
        data = self.get_callback_data(update)
        self.add_waiting_for("name", data)
        bot.send_message("What's your name?", self.command.settings.chat_id)

### Step 2 — confirm

class ConfirmName(Step):
    def handle(self, update):
        data = self.get_callback_data(update)
        name = data["name"]

        yes = self.next_step_callback(confirm=True, **data)
        no = self.current_step_callback(confirm=False, **data)

        keyboard = [
            [{"text": f"Confirm {name}", "callback_data": yes}],
            [{"text": "Change name", "callback_data": no}],
        ]

        bot.send_message(
            f"Is your name '{name}'?",
            self.command.settings.chat_id,
            reply_markup={"inline_keyboard": keyboard},
        )

### Step 3 — finish

class RegistrationDone(Step):
    def handle(self, update):
        data = self.get_callback_data(update)
        name = data["name"]
        bot.send_message(f"Welcome, {name}! 🎉", self.command.settings.chat_id)
        return self.command.finish(self.name, update)

---

## 🧪 Testing

Use TelegramTestCase:

class TestSignup(TelegramTestCase):
    def test_full_flow(self):
        self.send_text("/signup")
        self.send_text("Alice")
        self.click_on_text("Confirm Alice")
        self.verify_message_log([
            "What's your name?",
            "Is your name 'Alice'?",
            "Welcome, Alice! 🎉",
        ])

---

## 🏁 Best Practices

- Give each step one responsibility  
- Use meaningful callback keys  
- Always use `maybe_add_previous_button` when appropriate  
- Use `add_waiting_for` only for typed input  
- Always finish the command at the last step  

---

## 🛑 Common Mistakes

- Forgetting to set `steps_back=1`  
- Overwriting `data` accidentally  
- Forgetting to call `finish()`  
- Assuming all updates have message_id  
- Not including inline keyboards  

---

## 🎉 Summary

Commands let you build:

- multi-step flows  
- surveys  
- signup forms  
- settings pages  
- confirmation dialogs  
- typed + button interactions

with a clean, declarative API.
