"""Base command module to start telegram commands.

Note:
This module's command-class does not create an actual CLI command, but can be used by actual commands.
"""

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import override

from django_telegram_app.bot.bot import handle_update
from django_telegram_app.conf import settings as app_settings
from django_telegram_app.resolver import get_telegram_settings_model


class BaseTelegramCommand(BaseCommand):
    """Base command class to start Telegram bot commands."""

    command_text: str = ""

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--force",
            action="store_true",
            default=False,
            help="Force the command to run, regardless of the should_run outcome.",
        )

    def handle(self, *_args, **options):
        """Start the configured telegram command.

        Note:
        The chat_id is configured on the user as a TelegramSetting.
        A fake update is created with a message containing the command, this is not persisted.
        """
        if not self.command_text:
            raise ValueError("The attribute command_text must be set.")

        if not options["force"] and not self.should_run():
            return

        for telegram_settings in get_telegram_settings_model().objects.filter(user__is_active=True):
            user_language = get_user_language(telegram_settings.user)
            with override(user_language, deactivate=True):
                update = {"message": {"chat": {"id": telegram_settings.chat_id}, "text": self.command_text}}
                handle_update(update=update)
            self.stdout.write(self.style.SUCCESS(f"Started the command for {telegram_settings.user}."))

    def should_run(self) -> bool:
        """Determine if the command should run."""
        return True


def get_user_language(user) -> str:
    """Get the language code for a user.

    Look for various attributes on the user model to determine the preferred language.
    If no language attribute is found, the default LANGUAGE_CODE from settings is returned.

    The attribute names to look for can be configured in the TELEGRAM.USER_LANGUAGE_ATTRS setting.
    """
    for attr in app_settings.USER_LANGUAGE_ATTRS:
        value = getattr(user, attr, "")
        if value:
            return value

    return settings.LANGUAGE_CODE
