# Writing a custom management command
Django telegram app provides a base management command (BaseTelegramCommand) to facilitate calling telegram commands using `manage.py`.
This command automatically activates (and later deactivates) the user's configured language (fallback to settings.LANGUAGE_CODE).
Another specificity is that the class provides a should_run function which should return a boolean. This could be useful when the command is configured to run daily using a cronjob, but should not run on specific days.

The command is started for each active user that has TelegramSettings linked.

An example of a custom management command:
```python
# {appname}/management/commands/customcommand.py
"""Django command to start the bot's customcommand."""

from django.utils import timezone

from django_telegram_app.management.base import BaseTelegramCommand


class Command(BaseTelegramCommand):
    """Start the customcommand command."""

    help = "Start the customcommand command to ask users yes or no."
    command_text = "/customcommand"

    def should_run(self):
        """Only run the command if it's the last day of the month."""
        today = timezone.now().date()
        tomorrow = today + timezone.timedelta(days=1)
        return tomorrow.day == 1

```
