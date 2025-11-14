"""Poll command for the sample bot."""

from django_telegram_app.bot import bot
from django_telegram_app.bot.base import BaseCommand, Step, TelegramUpdate


class Command(BaseCommand):
    """Poll command."""

    description = "Poll for a user's favourite sport."

    @property
    def steps(self):
        """Return the steps of the command."""
        return [AskFavouriteSport(self), Confirm(self, steps_back=1), Respond(self)]


class AskFavouriteSport(Step):
    """Ask favourite sport step."""

    def handle(self, telegram_update: TelegramUpdate):
        """Handle the step."""
        data = self.get_callback_data(telegram_update)
        current_page: int = data.get("current_page", 1)
        start = (current_page - 1) * 3
        end = start + 3
        data.pop("favourite_sport", None)  # Remove any previous selection
        options = self.get_possible_answers()
        keyboard = [
            [{"text": text, "callback_data": self.next_step_callback(**data, favourite_sport=value)}]
            for text, value in options[start:end]
        ]
        self._maybe_add_pagination_buttons(keyboard, options, data, current_page, end=end)
        self.maybe_add_previous_button(keyboard, **data)
        bot.send_message(
            "What is your favourite sport?",
            self.command.settings.chat_id,
            reply_markup={"inline_keyboard": keyboard},
            message_id=telegram_update.message_id,
        )

    def get_possible_answers(self):
        """Get the possible options for the poll command."""
        return [
            ("🏓 Ping Pong", "Ping Pong"),
            ("🤺 Fencing", "Fencing"),
            ("🏸 Badminton", "Badminton"),
            ("🥊 Boxing", "Boxing"),
            ("🏹 Archery", "Archery"),
            ("🏒 Hockey", "Hockey"),
        ]

    def _maybe_add_pagination_buttons(self, keyboard: list, days: list, data: dict, current_page: int, end: int):
        if current_page > 1:
            data_back = dict(data, current_page=current_page - 1)
            keyboard.append([{"text": "⬅️ Back", "callback_data": self.current_step_callback(**data_back)}])
        if len(days) > end:
            data_next = dict(data, current_page=current_page + 1)
            keyboard.append([{"text": "➡️ Next", "callback_data": self.current_step_callback(**data_next)}])


class Confirm(Step):
    """Confirm step."""

    def handle(self, telegram_update: TelegramUpdate):
        """Handle the step."""
        data = self.get_callback_data(telegram_update)
        favourite_sport = data["favourite_sport"]
        data_yes = dict(data, confirmed=True)
        data_no = dict(data, confirmed=False, cancel_text="Poll cancelled. Your favourite sport was not recorded.")
        keyboard = [
            [{"text": "✅ Yes", "callback_data": self.next_step_callback(**data_yes)}],
            [{"text": "❌ No", "callback_data": self.cancel_callback(**data_no)}],
        ]
        self.maybe_add_previous_button(keyboard, **data)
        bot.send_message(
            f"Would you like to submit {favourite_sport} as your favourite sport?",
            self.command.settings.chat_id,
            reply_markup={"inline_keyboard": keyboard},
            message_id=telegram_update.message_id,
        )


class Respond(Step):
    """Respond step."""

    def handle(self, telegram_update: TelegramUpdate):
        """Handle the step."""
        data = self.get_callback_data(telegram_update)
        favourite_sport = data["favourite_sport"]
        bot.send_message(
            f"Thank you! Your favourite sport {favourite_sport} has been recorded.",
            self.command.settings.chat_id,
            message_id=telegram_update.message_id,
        )
        self.command.next_step(self.name, telegram_update)
