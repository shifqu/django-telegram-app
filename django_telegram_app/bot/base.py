"""Base classes for writing telegrambot commands.

telegrambot commands are named commands which can execute operations in response to user messages.
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, cast

from django_telegram_app.models import CallbackData

if TYPE_CHECKING:
    from django_telegram_app.models import AbstractTelegramSettings


class BaseCommand:
    """Represent a base Telegram bot command.

    This is the base class for all user-defined Telegram bot commands.
    """

    description: str

    def __init__(self, settings: AbstractTelegramSettings):
        """Initialize the command."""
        self.settings = settings

    def start(self, telegram_update: TelegramUpdate):
        """Start the command."""
        logging.info(f"Starting {self.get_name()} for user {self.settings.user}")
        self._clear_state()
        return self.steps[0].handle(telegram_update)

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
        cancel_text = data.get("cancel_text", "Command canceled.")
        send_message(cancel_text, self.settings.chat_id)
        return self.finish(current_step_name, telegram_update)

    def next_step(self, current_step_name: str, telegram_update: TelegramUpdate):
        """Proceed to the next step in the command."""
        next_index = self._steps_to_str().index(current_step_name) + 1
        if next_index < len(self.steps):
            next_step = self.steps[next_index]
            return next_step.handle(telegram_update)
        self.finish(current_step_name, telegram_update)

    def previous_step(self, current_step_name: str, telegram_update: TelegramUpdate):
        """Return to the previous step in the command."""
        data = self.get_callback_data(telegram_update.callback_data)
        steps_back = int(data.get("_steps_back", 1))
        previous_index = self._steps_to_str().index(current_step_name) - steps_back
        if previous_index >= 0:
            previous_step = self.steps[previous_index]
            return previous_step.handle(telegram_update)

    def current_step(self, current_step_name: str, telegram_update: TelegramUpdate):
        """Reload the current step."""
        current_index = self._steps_to_str().index(current_step_name)
        current_step = self.steps[current_index]
        return current_step.handle(telegram_update)

    def create_callback(self, step_name: str, action: str, **kwargs):
        """Create callback data for the current command and return the token."""
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

    def __init__(self, command: BaseCommand, steps_back: int = 0, unique_id: str | None = None):
        """Initialize the step."""
        self.command = command
        self.steps_back = steps_back
        self.unique_id = unique_id

    def handle(self, telegram_update: TelegramUpdate):
        """Handle the step."""
        raise NotImplementedError("This method should be overridden by subclasses.")

    def next_step_callback(self, **kwargs):
        """Create a callback to advance to the next step."""
        return self._create_callback("next_step", **kwargs)

    def previous_step_callback(self, **kwargs):
        """Create a callback to return to the previous step."""
        return self._create_callback("previous_step", **kwargs)

    def current_step_callback(self, **kwargs):
        """Create a callback to reload the current step with the provided data."""
        return self._create_callback("current_step", **kwargs)

    def cancel_callback(self, **kwargs):
        """Create a callback to cancel the command."""
        return self._create_callback("cancel", **kwargs)

    def maybe_add_previous_button(self, keyboard: list, **data):
        """Add a previous button to the provided keyboard if allowed."""
        if not self.steps_back:
            return
        data["_steps_back"] = self.steps_back
        keyboard.append([{"text": "⬅️ Previous step", "callback_data": self.previous_step_callback(**data)}])

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

    def add_waiting_for(self, message_key: str, data: dict[str, Any]):
        """Add waiting_for to the command settings.

        The message_key will be used to store the user input in the callback data of the next step.
        """
        data["_message_key"] = message_key
        self.command.settings.data["_waiting_for"] = self.next_step_callback(**data)
        self.command.settings.save()

    @property
    def name(self):
        """Return the name of the step."""
        return self.unique_id or type(self).__name__

    def _create_callback(self, action, **kwargs):
        """Create callback data for the current step and return the token."""
        return self.command.create_callback(self.name, action, **kwargs)


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
        elif self.callback_query:
            self.chat_id = int(self.callback_query["message"]["chat"]["id"])
            self.message_id = int(self.callback_query["message"]["message_id"])
            self.message_text = ""
            self.callback_data = str(self.callback_query.get("data"))
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
