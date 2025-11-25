# 📝 Writing a custom management command
**django-telegram-app** provides a base management command, `BaseManagementCommand`, that makes it easy to run Telegram bot commands using Django’s `manage.py`.

## What BaseManagementCommand does for you
- Provides a `should_run()` hook that returns a boolean.  
This is helpful when a command is scheduled (e.g., daily via cron) but should only run on certain days.
- Provides a `get_telegram_settings_filter()` hook to filter telegram settings.
This is helpful when a command should only be run for specific telegram_settings.
- Provides a `handle_command` hook to customize the update handling.
This is useful if you'd like to customize the update that was sent or do extra things like activate a specific language, etc...

---

## How the command is executed
When invoked, the management command runs once for each TelegramSettings instance, respecting the filter provided from `get_telegram_settings_filter()`.

---

## Avoiding Naming Conflicts
Since Django also uses a class named `Command` for management commands, it’s best to import your Telegram command under an alias:
```python title="myapp/management/commands/startcustomcommand.py"
from myapp.telegrambot.commands.customcommand import Command as CustomCommand
```

---

## Create a custom base management command for repeated logic
When using a swapped TelegramSettings model, you may find yourself overriding get_telegram_settings_filter() and related logic in every management command. To avoid duplication, define your own project-specific base command and subclass it throughout your project.
For example:
```python title="myapp/management/base.py"
...
class CustomBaseManagementCommand(BaseManagementCommand):
    """Base command for telegram management commands."""

    def get_telegram_settings_filter(self):
        """Filter to get only active users."""
        return {"user__is_active": True}

    def handle_command(self, telegram_settings: AbstractTelegramSettings, command_text: str):
        """Handle the update in the current user's language."""
        assert isinstance(telegram_settings, CustomTelegramSettings)
        assert isinstance(telegram_settings.user, CustomUser)

        update = {"message": {"chat": {"id": telegram_settings.chat_id}, "text": command_text}}
        with override(telegram_settings.user.language):
            handle_update(update, telegram_settings)

```
Then, in your actual management commands, subclass `CustomBaseManagementCommand` instead of `BaseManagementCommand` to keep your code clean and consistent.

---

## Example: custom management command
```python title="myapp/management/commands/startcustomcommand.py"
"""Django command to start the bot's customcommand."""

from django.utils import timezone

from django_telegram_app.management.base import BaseManagementCommand

from myapp.telegrambot.commands.customcommand import Command as CustomCommand


class Command(BaseManagementCommand):
    """Start the customcommand command."""

    help = "Start the customcommand command."
    command = CustomCommand

    def should_run(self):
        """Only run the command if it's the last day of the month."""
        today = timezone.now().date()
        tomorrow = today + timezone.timedelta(days=1)
        return tomorrow.day == 1

```
