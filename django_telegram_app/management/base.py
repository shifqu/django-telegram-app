"""Base command module to start telegram commands.

Note:
    This module's command-class does not create an actual CLI command, but can be used by actual commands.
"""

from django.core.management.base import BaseCommand

from django_telegram_app import get_telegram_settings_model
from django_telegram_app.bot.base import BaseBotCommand
from django_telegram_app.bot.bot import handle_update
from django_telegram_app.models import AbstractTelegramSettings


class BaseManagementCommand(BaseCommand):
    """Base command class to start Telegram bot commands.

    Subclasses can override:
        - the `should_run` method to determine if the command should run.
        - the `get_telegram_settings_filter` method to filter telegram settings.
        - the `handle_command` method to customize the update handling
    """

    command: type[BaseBotCommand] | None = None

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

        This method should not be overridden by subclasses.

        Subclasses can override:
            - the `should_run` method to determine if the command should run.
            - the `get_telegram_settings_filter` method to filter telegram settings.
            - the `handle_command` method to customize the update handling
        """
        if not self.command:
            raise ValueError("The attribute `command` must be set.")
        command_text = self.command.get_command_string()

        if not options["force"] and not self.should_run():
            self.stdout.write(self.style.NOTICE(f"Command '{command_text}' skipped as `should_run` returned False."))
            return

        telegram_settings_filter = self.get_telegram_settings_filter()
        telegram_settings_list = get_telegram_settings_model().objects.filter(**telegram_settings_filter)
        for telegram_settings in telegram_settings_list:
            self.handle_command(telegram_settings, command_text)
            self.stdout.write(self.style.SUCCESS(f"Started {self.command.get_name()} for {telegram_settings}."))

        if not telegram_settings_list:
            self.stdout.write(self.style.NOTICE("No Telegram-settings found for the given filter. Nothing to do."))

    def should_run(self) -> bool:
        """Determine if the command should run."""
        return True

    def get_telegram_settings_filter(self):
        """Get the filter to apply when retrieving telegram settings.

        Can be overridden by subclasses to filter telegram settings.
        By default, all telegram settings are returned.
        """
        return {}

    def handle_command(self, telegram_settings: AbstractTelegramSettings, command_text: str):
        """Construct a telegram update and handle it.

        Subclasses are encouraged to override this method to customize the update handling.
        (e.g., to add custom data to the update, to localize, etc.)

        Note:
            A minimal update is created with a message containing the command, this update is not persisted.
        """
        update = {"message": {"chat": {"id": telegram_settings.chat_id}, "text": command_text}}
        handle_update(update=update, telegram_settings=telegram_settings)
