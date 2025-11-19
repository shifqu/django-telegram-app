# 🚀 Getting started

This guide walks you through installing **django-telegram-app**, configuring your bot, and receiving your first Telegram update.

!!! note "**Prerequisite**"
    This guide assumes you already have a working Django project.  
    If you’re new to Django, start with [the official tutorial](https://docs.djangoproject.com/en/stable/intro/tutorial01/).

---

## 1. Install the package

(Optional) Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

Install from PyPI:

```bash
pip install django-telegram-app
```

---

## 2. Add the app to `INSTALLED_APPS`

In your Django `settings.py`:

```python
INSTALLED_APPS = [
    ...,
    "django_telegram_app",
]
```

---

## 3. (Optional) Create your own TelegramSettings model

Most real projects need additional fields such as preferences, or links
to internal models (users, companies, etc.).

Create your own concrete model:

```python
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_telegram_app.models import AbstractTelegramSettings


class TelegramSettings(AbstractTelegramSettings):
    """Custom Telegram settings model."""(swappable-telegram-settings.md)

    user = models.OneToOneField(settings.AUTH_USER_MODEL](), on_delete=models.CASCADE, verbose_name=_("user"))

```

Then set the following the root of the project's `settings.py`:

```python
TELEGRAM_SETTINGS_MODEL = "myapp.TelegramSettings"
```

See [**Telegram settings model**](swappable-telegram-settings.md) for the full guide.

---

##[ 4. Configure]() your Telegram bot

!!! note
    To learn how to obtain a bot token, visit the [official telegram tutorial](https://core.telegram.org/bots/tutorial#obtain-your-bot-token)

At minimum, you must provide the `BOT_URL`:

```python
TELEGRAM = {
    "BOT_URL": "https://api.telegram.org/bot123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11/"
}
```

See [**Configuration**](configuration.md) for the full list of settings.

---

## 5. Add the webhook URL to your project’s `urls.py`

django-telegram-app handles Telegram’s POST updates through a configurable webhook.

Add this to your root URLconf:

```python
from django.urls import include, path
from django_telegram_app.conf import settings as telegram_app_settings

urlpatterns = [
    ...,
    path(
        telegram_app_settings.ROOT_URL,           # e.g. "telegram/"
        include("django_telegram_app.urls"),      # webhook lives here
    ),
]
```

You could also access this setting by using `django.conf.settings.TELEGRAM["ROOT_URL]`

---

## 6. Run migrations

```bash
python manage.py migrate
```

This creates the tables for the default `TelegramSettings` model.

!!! note
    Most projects should override this model to add their own fields as outlined in [the optional step 3](#3-optional-create-your-own-telegramsettings-model).

---

## 7. Register your webhook with Telegram

Use the provided management command:

    python manage.py setwebhook https://example.com

Defaults to:

    <base_url>/telegram/webhook

---

## 8. Start creating bot commands

A minimal command (`roll.py`):
```python
from django_telegram_app.telegrambot.base import BaseCommand, Step, TelegramUpdate


class Command(BaseCommand):
    """A command that rolls a dice."""
    
    description = "A command that rolls a dice."

    @property
    def steps(self):
        return [DiceRoll(self)]


class DiceRoll(Step):
    """Dice roll step."""

    def handle(self, telegram_update: TelegramUpdate):
        """Roll the dice."""
        import random
        data = self.get_callback_data(telegram_update)
        dice_roll = random.randint(1, 6)
        bot.send_message(
            f"You rolled: {dice_roll}",
            self.command.settings.chat_id,
            message_id=telegram_update.message_id,
        )
        self.command.finish(self.name, telegram_update)
```

See [**Commands & bots**](bot-commands.md) for more information and examples.

---

# 🎉 That’s it — your bot is ready

You now have:

- django-telegram-app installed  
- a working webhook  
- migrations applied  
- commands ready to be discovered  

From here, continue with:

- [**Telegram settings model**](swappable-telegram-settings.md) → customize chat/user storage  
- [**Commands & bots**](bot-commands.md) → write reusable bot commands  
- [**Configuration**](configuration.md) → all available settings  
- [**Management commands**](management-commands.md) → start commands using manage.py
- [**Testing**](testing.md) → use `TelegramTestCase` to test your bot logic  

Enjoy building your Telegram bot inside Django!
