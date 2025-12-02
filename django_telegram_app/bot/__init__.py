"""Bot module for the Telegram app."""

from __future__ import annotations

import functools
import pkgutil
from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING

from django.apps import apps
from django.conf import settings

if TYPE_CHECKING:
    from django_telegram_app.bot.base import BaseBotCommand
    from django_telegram_app.models import AbstractTelegramSettings


def find_commands(telegrambot_dir: Path):
    """Return a list of all the command names that are available for the provided telegrambot path."""
    command_dir = telegrambot_dir / "commands"
    return [name for _, name, is_pkg in pkgutil.iter_modules([command_dir]) if not is_pkg and not name.startswith("_")]


def get_command_class(app_name: str, name: str) -> type[BaseBotCommand]:
    """Return the Command class for the given command name and application name.

    Allow all errors raised by the import process (ImportError, AttributeError) to propagate.
    """
    module = import_module(f"{app_name}.telegrambot.commands.{name}")
    return module.Command


def load_command_class(app_name: str, name: str, settings: AbstractTelegramSettings) -> BaseBotCommand:
    """Return the Command class instance for the given command name and application name.

    Allow all errors raised by the import process (ImportError, AttributeError) to propagate.
    """
    Command = get_command_class(app_name, name)
    return Command(settings)


@functools.cache
def get_commands():
    """Return a dictionary mapping command names to their callback applications.

    Look for a telegrambot.commands package in each installed application -- if a commands package exists, register all
    commands in that package.

    All user-defined commands from the specified settings module are included.

    The dictionary is in the format {command_name: app_name}. Key-value
    pairs from this dictionary can then be used in calls to
    load_command_class(app_name, command_name)

    The dictionary is cached on the first call and reused on subsequent
    calls.
    """
    commands: dict[str, str] = {}
    if not settings.configured:
        return commands

    for app_config in apps.get_app_configs():
        path = Path(app_config.path) / "telegrambot"
        commands.update({name: app_config.name for name in find_commands(path)})

    return commands
