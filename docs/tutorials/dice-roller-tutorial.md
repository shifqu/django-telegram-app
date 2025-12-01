# 🎲 Your First Command: the dice roller

This tutorial starts where [getting started](getting-started.md) left off. You’ll build a simple **D&D-style dice roller** for your Telegram bot using `django-telegram-app`.

By the end, your bot will:

- respond to `/roll`
- let the user choose a die (`d4`, `d6`, `d8`, `d10`, `d12`, `d20`)
- display the result
- offer a “Roll again” and "Choose another die" button

This assumes you already:

- have a Django project
- configured `django_telegram_app` (installed app, `TELEGRAM` settings, webhook set)
- can send `/start` or some basic command to the bot successfully

---

## 1. Create a new Django app for dice

From your project root:

```
python manage.py startapp dice
```

Add it to `INSTALLED_APPS` in `settings.py`:

```python title="mysite/settings.py"
INSTALLED_APPS = [
    # ...
    "django_telegram_app",
    "dice",
]
```

We’ll keep everything for this tutorial inside the `dice` app.

---

## 2. Create the telegrambot command structure

Inside the `dice` app, create the following directories:

```bash
mkdir -p dice/telegrambot/commands
touch dice/telegrambot/__init__.py
touch dice/telegrambot/commands/__init__.py
```

Your file tree should now look like:

```
dice/
    __init__.py
    admin.py
    apps.py
    models.py
    telegrambot/
        __init__.py
        commands/
            __init__.py
```

Commands are discovered from `dice/telegrambot/commands/`, so we just need to add a `roll.py` module there.

---

## 3. Implement the `/roll` command

Create `dice/telegrambot/commands/roll.py`:

```python title="dice/telegrambot/commands/roll.py"
"""Roll command for the Telegram bot."""

import random

from django_telegram_app.bot import bot
from django_telegram_app.bot.base import BaseBotCommand, Step, TelegramUpdate


class Command(BaseBotCommand):
    """Dice rolling command.

    Triggered by the /roll command.
    """

    description = "Roll a D&D-style die (d4, d6, d8, d10, d12, d20)."

    @property
    def steps(self):
        """Return the steps of the command."""
        return [ChooseDie(self), ShowResult(self)]


class ChooseDie(Step):
    """Let the user choose which die to roll."""

    def handle(self, telegram_update: TelegramUpdate):
        """Send a keyboard with available dice options."""
        data = self.get_callback_data(telegram_update)

        keyboard = [
            [
                {"text": "🎲 d4", "callback_data": self.next_step_callback(data, sides=4)},
                {"text": "🎲 d6", "callback_data": self.next_step_callback(data, sides=6)},
            ],
            [
                {"text": "🎲 d8", "callback_data": self.next_step_callback(data, sides=8)},
                {"text": "🎲 d10", "callback_data": self.next_step_callback(data, sides=10)},
            ],
            [
                {"text": "🎲 d12", "callback_data": self.next_step_callback(data, sides=12)},
                {"text": "🎲 d20", "callback_data": self.next_step_callback(data, sides=20)},
            ],
        ]

        bot.send_message(
            "Choose a die to roll:",
            self.command.settings.chat_id,
            reply_markup={"inline_keyboard": keyboard},
            message_id=telegram_update.message_id,
        )


class ShowResult(Step):
    """Roll the die and display the result."""

    def handle(self, update: TelegramUpdate):
        """Roll the chosen die and show the outcome with buttons."""
        data = self.get_callback_data(update)
        sides = int(data["sides"])

        result = random.randint(1, sides)

        previous_step_callback = self.previous_step_callback(steps_back=1, original_data=data)
        keyboard = [
            [{"text": "🔁 Roll again", "callback_data": self.current_step_callback(data)}],
            [{"text": "🎯 Choose another die", "callback_data": previous_step_callback}],
        ]

        bot.send_message(
            f"You rolled *{result}* on a d{sides}! 🎉",
            self.command.settings.chat_id,
            reply_markup={"inline_keyboard": keyboard},
            message_id=update.message_id,
        )

```

At this point, you have a working command:

- `/roll` → shows a list of dice
- tapping a die → rolls that die and shows the result
- `Roll again` → rolls the same die again
- `Choose another die` → goes back to the die selection

## 4. Understanding the `/roll` command
### The Command class
- Commands subclasses `BaseBotCommand` and represents a single bot command, here `/roll`.
- The command name is inferred from the module name (`roll.py` → `/roll`).
- `description` is used in help contexts, so it’s good to keep it short and clear.
- `steps` (property) is a list of `Step` subclasses, they define the flow of the command.
- The command always starts with the first step in the list.
- `translate` is True by default and is used to activate the user's language. Steps can override this behaviour (see below)

### The steps
- Steps are subclasses of `Step` and represent a single step in the command.
- `translate` is None by default, which means the command's `translate` flag is used. If the step's `translate` flag is True or False, this value will be used instead.
- The `__call__` method of step is used as an entrypoint to start a step. It essentially activates translation and calls the `handle` method.
- Steps can:
    - request callback data based on the telegram_update's callback token,
    - create new callback data with data for the current step,
    - create a keyboard with buttons that contain this new callback data,
    - send feedback to the user using `bot.send_message`.
    - The new callback data can make the bot:
        - call the next step
        - call the previous step
        - call the current step again
        - cancel the command
        - finish the command

!!! note
    For more info on how callbacks work, see the [CallbackData topic](../topics/callback-data.md)

---

## Next steps

Continue to:

**[👉 Extending Your First Command](dice-roller-tutorial-ext.md)**