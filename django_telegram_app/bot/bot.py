"""Telegram bot core module."""

from typing import TYPE_CHECKING

import requests

from django_telegram_app.bot import get_commands, load_command_class
from django_telegram_app.bot.base import TelegramUpdate
from django_telegram_app.conf import settings
from django_telegram_app.models import CallbackData
from django_telegram_app.resolver import get_telegram_settings_model

if TYPE_CHECKING:
    from django_telegram_app.models import AbstractTelegramSettings

DO_NOTHING = "noop"


def is_valid_token(token: str | None):
    """Return whether the webhook token is valid.

    If no token is configured, the token is considered valid.

    Note:
        This token is not the CallbackData token but a token used to validate the webhook.
        This enables us to differentiate original telegram requests from spam
    """
    if not settings.WEBHOOK_TOKEN:
        return True
    return token == settings.WEBHOOK_TOKEN


def handle_update(update: dict):
    """Handle the update."""
    telegram_update = TelegramUpdate(update)
    telegram_settings = get_telegram_settings_model().objects.get(chat_id=telegram_update.chat_id)

    if telegram_update.is_command():
        _start_command_or_send_help(telegram_update, telegram_settings)
    elif telegram_update.is_callback_query():
        _call_command_step(telegram_update.callback_data, telegram_settings, telegram_update)
    elif telegram_settings.data.get("_waiting_for"):
        token = telegram_settings.data["_waiting_for"]
        _call_command_step(token, telegram_settings, telegram_update)
    else:
        send_help(telegram_update.chat_id, telegram_settings)


def send_help(chat_id: int, telegram_settings: "AbstractTelegramSettings"):
    """Send a help message to the user."""
    command_info_list = []
    for command_name, app_name in get_commands().items():
        command = load_command_class(app_name, command_name, telegram_settings)
        command_info_list.append(f"{command.get_command_string()} - {command.description}")

    commands_text = "\n".join(command_info_list)
    help_text = f"Currently available commands:\n{commands_text}"
    send_message(help_text, chat_id)


def send_message(text: str, chat_id: int, reply_markup: dict | None = None, message_id: int = 0):
    """Send a message to the user.

    If message_id is provided, it will edit the existing message instead.

    References:
    https://core.telegram.org/bots/api#sendmessage
    """
    payload = {"chat_id": chat_id, "text": text}
    endpoint = "sendMessage"
    if message_id:
        payload["message_id"] = message_id
        endpoint = "editMessageText"

    if reply_markup:
        payload["reply_markup"] = reply_markup
    post(endpoint, payload=payload)


def post(endpoint: str, payload: dict, timeout: int = 5):
    """Post the payload to the given endpoint."""
    url = _construct_endpoint(endpoint)
    response = requests.post(url, json=payload, timeout=timeout)
    response.raise_for_status()
    return response


@staticmethod
def _construct_endpoint(name: str):
    """Construct the endpoint for the given command."""
    root_url = settings.BOT_URL.rstrip("/")
    return f"{root_url}/{name}"


def _start_command_or_send_help(telegram_update: TelegramUpdate, telegram_settings: "AbstractTelegramSettings"):
    """Start a command or send help message."""
    command_name = telegram_update.message_text.split(maxsplit=1)[0]
    command_str = command_name.lstrip("/")
    try:
        app_name = get_commands()[command_str]
    except KeyError:
        send_help(telegram_update.chat_id, telegram_settings)
        return
    command_cls = load_command_class(app_name, command_str, telegram_settings)
    command_cls.start(telegram_update)


def _call_command_step(token: str, telegram_settings: "AbstractTelegramSettings", telegram_update: TelegramUpdate):
    """Call a command's step from the provided data.

    Return True if the step was called successfully, False otherwise.
    """
    if token == DO_NOTHING:
        return False

    try:
        data = CallbackData.objects.get(token=token)
    except CallbackData.DoesNotExist:
        send_message("This command has expired.", telegram_update.chat_id, message_id=telegram_update.message_id)
        return False

    command_name = data.command.lstrip("/")
    command_info = get_commands()[command_name]
    command = load_command_class(command_info, command_name, telegram_settings)
    getattr(command, data.action)(data.step, telegram_update)
    return True
