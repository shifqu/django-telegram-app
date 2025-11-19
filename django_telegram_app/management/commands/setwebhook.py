"""Django command to set a telegram webhook."""

import requests
from django.core.management.base import BaseCommand, CommandError

from django_telegram_app.conf import settings as app_settings


class Command(BaseCommand):
    """Set a telegram webhook."""

    help = "Sets the webhook for the telegram bot."

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "base_url",
            help="A publicly accessible base URL used to construct the Telegram webhook (e.g. 'https://example.com').",
        )

    def handle(self, *_args, **options):
        """Set a webhook.

        Notes: Once a webhook is set, getUpdates no longer works.

        References: https://core.telegram.org/bots/api#setwebhook
        """
        root_url = app_settings.BOT_URL.rstrip("/")
        endpoint = f"{root_url}/setWebhook"
        parts = [options["base_url"], app_settings.ROOT_URL, app_settings.WEBHOOK_URL]
        url = "/".join(part.strip("/") for part in parts if part)
        args = {"url": url}
        if app_settings.WEBHOOK_TOKEN:
            args["secret_token"] = app_settings.WEBHOOK_TOKEN
        response = requests.post(endpoint, json=args, timeout=5)
        response_json: dict = response.json()
        if not response_json.get("ok"):
            self.stderr.write(self.style.ERROR(f"Something went wrong while setting the webhook. {response_json}"))
            raise CommandError(f"Failed to set webhook to {url}.")
        self.stdout.write(self.style.SUCCESS(f'Successfully set webhook to "{url}"'))
