"""Base classes for writing telegrambot commands.

telegrambot commands are named commands which can execute operations in response to user messages.
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Sequence
from contextlib import nullcontext
from typing import TYPE_CHECKING, Any, cast

from django.utils.translation import gettext as _
from django.utils.translation import override

from django_telegram_app.models import CallbackData

if TYPE_CHECKING:
    from django_telegram_app.models import AbstractTelegramSettings


class BaseBotCommand:
    """Represent a base Telegram bot command.

    This is the base class for all user-defined Telegram bot commands.
    """

    description: str = ""
    exclude_from_help: bool = False
    translate: bool = True

    def __init__(self, settings: AbstractTelegramSettings):
        """Initialize the command."""
        self.settings = settings

    def start(self, telegram_update: TelegramUpdate):
        """Start the command."""
        logging.info(f"Starting {self.get_name()} for {self.settings}")
        self._clear_state()
        return self.steps[0](telegram_update)

    def finish(self, current_step_name: str, telegram_update: TelegramUpdate):
        """Finish the command and clear all data."""
        logging.info(f"Finishing the command at step {current_step_name}")
        self._clear_state()
        self._clear_callback_data(telegram_update)

    def cancel(self, current_step_name: str, telegram_update: TelegramUpdate):
        """Cancel the command and clear all data."""
        from django_telegram_app.bot.bot import send_message

        logging.info(f"Canceled the command at step {current_step_name}")
        data = self.get_callback_data(telegram_update.callback_data)
        with override(telegram_update.language_code):
            cancel_text = data.get("cancel_text", _("Command canceled."))
        send_message(cancel_text, self.settings.chat_id)
        return self.finish(current_step_name, telegram_update)

    def next_step(self, current_step_name: str, telegram_update: TelegramUpdate):
        """Proceed to the next step in the command."""
        next_index = self._steps_to_str().index(current_step_name) + 1
        if next_index < len(self.steps):
            next_step = self.steps[next_index]
            return next_step(telegram_update)
        self.finish(current_step_name, telegram_update)

    def previous_step(self, current_step_name: str, telegram_update: TelegramUpdate):
        """Return to the previous step in the command."""
        data = self.get_callback_data(telegram_update.callback_data)
        steps_back = int(data.get("_steps_back", 1))
        previous_index = self._steps_to_str().index(current_step_name) - steps_back
        if previous_index >= 0:
            previous_step = self.steps[previous_index]
            return previous_step(telegram_update)

    def current_step(self, current_step_name: str, telegram_update: TelegramUpdate):
        """Reload the current step."""
        current_index = self._steps_to_str().index(current_step_name)
        current_step = self.steps[current_index]
        return current_step(telegram_update)

    def create_callback(self, step_name: str, action: str, **kwargs):
        """Create callback data for the current command and return the token."""
        if not kwargs:
            kwargs = self._get_default_callback_data()
        if "correlation_key" not in kwargs:
            kwargs.update(self._get_default_callback_data())
        callback_data = CallbackData(command=self.get_command_string(), step=step_name, action=action, data=kwargs)
        callback_data.save()
        return str(callback_data.token)

    def get_callback(self, token: str):
        """Return the callback for the given token."""
        return CallbackData.objects.get(token=token)

    def get_callback_data(self, callback_token: str) -> dict[str, Any]:
        """Get callback data from the callback token.

        If the callback token is not provided, return default callback data.
        """
        if not callback_token:
            return self._get_default_callback_data()
        callback_data = self.get_callback(callback_token)
        return callback_data.data

    @property
    def steps(self) -> Sequence[Step]:
        """Return the steps of the command."""
        raise NotImplementedError("Subclasses must implement this method")

    @classmethod
    def get_name(cls):
        """Return the name of the command.

        By default this is the lowercased last part of the module name.
        """
        return cls.__module__.split(".")[-1].lower()

    @classmethod
    def get_command_string(cls):
        """Return the command string."""
        return f"/{cls.get_name()}"

    def _get_default_callback_data(self):
        """Return a dictionary with correlation key as default callback data."""
        return {"correlation_key": str(uuid.uuid4())}

    def _clear_state(self):
        """Clear the command state."""
        self.settings.data = {}
        self.settings.save()

    def _clear_callback_data(self, telegram_update: TelegramUpdate):
        """Clear callback data for the current command."""
        step_data = self.get_callback_data(telegram_update.callback_data)
        correlation_key = step_data.get("correlation_key", "non_existent_key")
        CallbackData.objects.filter(data__correlation_key=correlation_key).delete()

    def _steps_to_str(self):
        return [step.name for step in self.steps]


class Step:
    """Represent a step in a Telegram bot command.

    This is the base class for all user-defined steps.
    """

    def __init__(self, command: BaseBotCommand, unique_id: str | None = None, translate: bool | None = None):
        """Initialize the step.

        Args:
            command: The command this step belongs to.
            unique_id: An optional unique identifier for the step. If not provided, the class name will be used.
            translate: Whether to activate translation for this step. If None, the command's translate setting will be
                       used. If True or False, it will override the command's setting.
        """
        self.command = command
        self.unique_id = unique_id
        self.translate = translate

    def __call__(self, telegram_update: TelegramUpdate):
        """Execute the step.

        This activates the appropriate translation based on the user's language code.
        """
        if self.translate is None:
            should_translate = self.command.translate
        else:
            should_translate = self.translate

        translation_override = override(telegram_update.language_code) if should_translate else nullcontext()
        with translation_override:
            return self.handle(telegram_update)

    def handle(self, telegram_update: TelegramUpdate):
        """Handle the step."""
        raise NotImplementedError("This method should be overridden by subclasses.")

    def next_step_callback(self, original_data: dict | None = None, **kwargs):
        """Create a callback to advance to the next step."""
        return self._create_callback("next_step", original_data, **kwargs)

    def previous_step_callback(self, steps_back: int, original_data: dict | None = None, **kwargs):
        """Create a callback to return to the previous step."""
        kwargs["_steps_back"] = steps_back
        return self._create_callback("previous_step", original_data, **kwargs)

    def current_step_callback(self, original_data: dict | None = None, **kwargs):
        """Create a callback to reload the current step with the provided data."""
        return self._create_callback("current_step", original_data, **kwargs)

    def cancel_callback(self, original_data: dict | None = None, **kwargs):
        """Create a callback to cancel the command."""
        return self._create_callback("cancel", original_data, **kwargs)

    def get_callback_data(self, telegram_update: TelegramUpdate):
        """Get callback data from the telegram_update.

        If the update is a message and not a command, check if we are waiting for user input.
        If so, retrieve the callback data using the waiting_for token and store the message text
        in the appropriate key in the callback data.

        Otherwise, retrieve the callback data using the callback token from the update.
        If no callback token is provided, return default callback data.
        """
        if not telegram_update.callback_data and telegram_update.is_message() and not telegram_update.is_command():
            waiting_for = self.command.settings.data.get("_waiting_for", None)
            if waiting_for:
                callback_token = waiting_for
                callback_data = self.command.get_callback_data(callback_token)
                key = callback_data["_message_key"]  # Move the message_text to this key
                callback_data[key] = telegram_update.message_text.strip()
                return callback_data

        callback_token = telegram_update.callback_data
        return self.command.get_callback_data(callback_token)

    def add_waiting_for(self, message_key: str, data: dict[str, Any] | None = None):
        """Add waiting_for to the command settings.

        The message_key will be used to store the user input in the callback data of the next step.
        """
        data = data or {}
        self.command.settings.data["_waiting_for"] = self.next_step_callback(data, _message_key=message_key)
        self.command.settings.save()

    @property
    def name(self):
        """Return the name of the step."""
        return self.unique_id or type(self).__name__

    def _create_callback(self, action: str, original_data: dict | None = None, **kwargs):
        """Create callback data for the current step and return the token."""
        original_data = original_data or {}
        data = {**original_data, **kwargs}
        return self.command.create_callback(self.name, action, **data)


class TelegramUpdate:
    """Represent a normalized Telegram update."""

    def __init__(self, update: dict):
        """Initialize the normalized Telegram update."""
        self.message = cast(dict | None, update.get("message"))
        self.callback_query = cast(dict | None, update.get("callback_query"))

        if self.message and "text" in self.message:
            self.chat_id = int(self.message["chat"]["id"])
            self.message_id = 0
            self.message_text = str(self.message["text"])
            self.callback_data = ""
            self.language_code = str(self.message.get("from", {}).get("language_code", "")) or None
        elif self.callback_query:
            self.chat_id = int(self.callback_query["message"]["chat"]["id"])
            self.message_id = int(self.callback_query["message"]["message_id"])
            self.message_text = ""
            self.callback_data = str(self.callback_query.get("data"))
            self.language_code = str(self.callback_query["from"].get("language_code", "")) or None
        else:
            raise ValueError("Unsupported Telegram update format")

    def is_message(self):
        """Return the message part of the update."""
        return self.message is not None

    def is_callback_query(self):
        """Return the callback query part of the update."""
        return self.callback_query is not None

    def is_command(self):
        """Check if the update is a command."""
        return self.is_message() and self.message_text.startswith("/")
