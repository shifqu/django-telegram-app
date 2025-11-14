# 📝 Writing a custom management command
django-telegram-app provides a base management command, `BaseTelegramCommand`, that makes it easy to run Telegram bot commands using Django’s `manage.py`.

## What BaseTelegramCommand does for you
- **Activates the user’s preferred language** (with `settings.LANGUAGE_CODE` as a fallback) before running the command, and deactivates it afterward.
- Provides a `should_run()` hook that returns a boolean.  
This is helpful when a command is scheduled (e.g., daily via cron) but should only run on certain days.

## How the command is executed
When invoked, the management command runs once for each active user who has a TelegramSettings instance linked.

## Tip: Avoid Naming Conflicts
Since Django also uses a class named `Command` for management commands, it’s best to import your Telegram command under an alias:
```python
from apps.myapp.telegrambot.commands.customcommand import Command as CustomCommand
```

## Example: custom management command
```python
# apps/myapp/management/commands/customcommand.py
"""Django command to start the bot's customcommand."""

from django.utils import timezone

from django_telegram_app.management.base import BaseTelegramCommand

from apps.myapp.telegrambot.commands.customcommand import Command as CustomCommand


class Command(BaseTelegramCommand):
    """Start the customcommand command."""

    help = "Start the customcommand command to ask users yes or no."
    command = CustomCommand

    def should_run(self):
        """Only run the command if it's the last day of the month."""
        today = timezone.now().date()
        tomorrow = today + timezone.timedelta(days=1)
        return tomorrow.day == 1

```
