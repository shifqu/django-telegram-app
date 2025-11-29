"""Hidden command for the sample bot."""

from django_telegram_app.bot.base import BaseBotCommand


class Command(BaseBotCommand):  # pylint: disable=abstract-method
    """Hidden command.

    steps are not defined because this command is never run, it exists only to test the exclude_from_help feature.
    """

    description = "A hidden command that does not appear in help."
    exclude_from_help = True
