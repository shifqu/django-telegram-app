"""Django command to set telegram commands."""

import requests
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import override

from django_telegram_app.bot import get_command_class, get_commands
from django_telegram_app.conf import settings as app_settings


class Command(BaseCommand):
    """Set telegram commands."""

    help = "Sets the commands for the telegram bot."

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--include-hidden",
            action="store_true",
            default=False,
            help="Add all commands, even those excluded from help.",
        )
        parser.add_argument(
            "--locale",
            type=str,
            action="append",
            help=(
                "Specify the locale (A two-letter ISO 639-1 language code) for which to set the commands, "
                "can be used multiple times."
            ),
        )
        parser.add_argument(
            "--delete",
            action="store_true",
            default=False,
            help="Clear the list of commands.",
        )

    def handle(self, *_args, **options):
        """Change the list of the bot's commands.

        References: https://core.telegram.org/bots/api#setmycommands
        """
        locales = options.get("locale")
        if options.get("delete", False):
            return self._deletecommands("deleteMyCommands", locales)

        include_hidden = options.get("include_hidden", False)
        self._setcommands("setMyCommands", include_hidden, locales)

    def _setcommands(self, api_method_name: str, include_hidden: bool, locales: list[str] | None):
        """Set the bot commands for specific locales.

        The locales list can be empty, which indicates the commands should be set without a locale.
        """
        command_info_list = self._get_command_info_list(include_hidden)
        payload: dict = {"commands": command_info_list}
        if not locales:
            return self._post(api_method_name, **payload)

        for locale in locales:
            with override(locale):
                command_info_list = self._get_command_info_list(include_hidden, clear_cache=True)
                payload: dict = {"commands": command_info_list, "language_code": locale}
                self._post(api_method_name, **payload)
        get_commands.cache_clear()  # Clear cache after locale-specific loading to avoid it being stuck in last locale.

    def _deletecommands(self, api_method_name: str, locales: list[str] | None):
        """Delete the bot commands for specific locales.

        The locales list can be empty, which indicates the commands should be deleted without a locale.
        """
        payload: dict = {}
        if not locales:
            return self._post(api_method_name, **payload)

        for locale in locales:
            payload["language_code"] = locale
            self._post(api_method_name, **payload)

    def _post(self, api_method_name: str, **kwargs):
        root_url = app_settings.BOT_URL.rstrip("/")
        endpoint = f"{root_url}/{api_method_name}"
        response = requests.post(endpoint, json=kwargs, timeout=5)
        response_json: dict = response.json()
        if not response_json.get("ok"):
            msg = f"Something went wrong while calling {api_method_name}.\n{response_json}"
            self.stderr.write(self.style.ERROR(msg))
            raise CommandError(msg)
        self.stdout.write(self.style.SUCCESS(f"Successfully called {api_method_name}."))

    def _get_command_info_list(self, include_hidden: bool, clear_cache: bool = False) -> list[dict[str, str]]:
        command_info_list = []
        if clear_cache:
            get_commands.cache_clear()
        for command_name, app_name in get_commands().items():
            command = get_command_class(app_name, command_name)
            if not include_hidden and command.exclude_from_help:
                continue
            command_info_list.append({"command": command.get_name(), "description": command.description})
        return command_info_list
