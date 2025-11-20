# 🤖 Writing a custom bot command

## Discovering commands
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
In this example, the `roll` command will be made available to any project that includes the `myapp` application in `INSTALLED_APPS`.  
The `_private.py` module will not be available as a management command.  
The `roll.py` module has a few requirements – it must define a class `Command` that extends `django_telegram_app.base.BaseCommand` or a subclass of it and should provide the property `steps` which returns a list of `Step` subclasses.

---

## Useful functions to call
Usually the first thing a step does is `self.get_callback_data`.

When keyboards are included, it's best to always call `self.maybe_add_previous_button` as it adds a button to go to a previous step if the step was initialized with the `steps_back` parameter.

---

## Example: A custom bot command
```python title="myapp/telegrambot/commands/customcommand.py"
"""CustomCommand for the telegram bot."""

from django_telegram_app import bot
from django_telegram_app.base import BaseCommand, Step, TelegramUpdate


class Command(BaseCommand):
    """Represent the customcommand command."""

    description = "Ask the user a simple question and provide yes/no buttons."

    @property
    def steps(self):
        """Return the steps of the command."""
        return [AskYesOrNo(self)]


class AskYesOrNo(Step):
    """Represent a custom step."""

    def handle(self, telegram_update: TelegramUpdate):
        """Handle the step."""
        data = self.get_callback_data(telegram_update)
        data_yes = dict(data, answer=True)
        data_no = dict(data, answer=False)
        keyboard = [
            [{"text": "✅ Yes", "callback_data": self.next_step_callback(**data_yes)}],
            [{"text": "❌ No", "callback_data": self.next_step_callback(**data_no)}],
        ]
        self.maybe_add_previous_button(keyboard, **data)
        bot.send_message(
            "Yes or no?",
            self.command.settings.chat_id,
            reply_markup={"inline_keyboard": keyboard},
            message_id=telegram_update.message_id,
        )

```