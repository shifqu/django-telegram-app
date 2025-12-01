"""Echo command for the sample bot."""

from django_telegram_app.bot import bot
from django_telegram_app.bot.base import BaseBotCommand, Step, TelegramUpdate


class Command(BaseBotCommand):
    """Echo command."""

    description = "Responds with the same message."

    @property
    def steps(self):
        """Return the steps of the command."""
        return [WaitForInput(self), Echo(self, translate=False)]


class WaitForInput(Step):
    """Wait for input step."""

    def handle(self, telegram_update: TelegramUpdate):
        """Handle the step."""
        self.add_waiting_for("userinput")
        bot.send_message(
            "Send the message you want to echo:", self.command.settings.chat_id, message_id=telegram_update.message_id
        )


class Echo(Step):
    """Echo step."""

    def handle(self, telegram_update: TelegramUpdate):
        """Handle the step."""
        data = self.get_callback_data(telegram_update)
        user_input = data["userinput"]
        bot.send_message(
            f"You said: {user_input}",
            self.command.settings.chat_id,
            message_id=telegram_update.message_id,
        )
        self.command.next_step(self.name, telegram_update)
