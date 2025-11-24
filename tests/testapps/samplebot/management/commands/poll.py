"""Django command to start the bot's poll command."""

from django_telegram_app.management.base import BaseManagementCommand
from tests.testapps.samplebot.telegrambot.commands.poll import Command as PollCommand


class Command(BaseManagementCommand):
    """Start the customcommand command."""

    help = "Start the customcommand command to ask users yes or no."
    command = PollCommand
