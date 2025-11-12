# django-telegram-app
A Django app to integrate Telegram bots into your project.

Detailed documentation is in the [`docs/`](https://github.com/shifqu/django-telegram-app/tree/main/docs/) directory.

---
[![Code style: Ruff](https://img.shields.io/badge/style-ruff-8b5000)](https://github.com/astral-sh/ruff)
[![Typing: Pyright](https://img.shields.io/badge/typing-pyright-725a42
)](https://github.com/RobertCraigie/pyright-python)
[![Linting: Pylint](https://img.shields.io/badge/typing-pylint-755147
)](https://github.com/pylint-dev/pylint)
[![Framework: Django](https://img.shields.io/badge/framework-django-727242)](https://docs.djangoproject.com/en/5.2/)
[![License](https://img.shields.io/github/license/mashape/apistatus.svg)](https://opensource.org/license/mit)
[![CI Validation](https://github.com/shifqu/django-telegram-app/actions/workflows/ci.yml/badge.svg)](https://github.com/shifqu/django-telegram-app/actions/workflows/ci.yml)

---

## Features

- ✅ Command-based bot architecture with step-based flow
- ✅ Swappable `TelegramSettings` model
- ✅ Inline admin integration for linking Telegram settings to users
- ✅ Extensible: add commands per app via auto-discovery
- ✅ Built-in system checks for misconfiguration
- ✅ Django ORM integration (no direct API handling required)
- ✅ Easy to test (includes custom TelegramTestCase)

## Requirements (officially supported)

- Python **3.10+**
- Django **5.2+**

## Quick start

1. Install the package
    ```bash
    pip install django-telegram-app
    ```

1. Add "django_telegram_app" to your INSTALLED_APPS setting like this:
    ```python
    INSTALLED_APPS = [
        ...,
        "django_telegram_app",
    ]
    ```

2. Include the telegram URLconf in your project urls.py like this:
    ```python
    ...
    from django_telegram_app.conf import settings as telegram_app_settings
    ...
    path(telegram_app_settings.ROOT_URL, include("django_telegram_app.urls")),
    ```

3. Create your own commands in each app under `{appname}/telegrambot/commands/`. Refer to the documentation for more details on how to write custom commands.

4. Add the provided telegramsettings inline to your user-model like this:
    ```python
    # user/admin.py
    from django_telegram_app.admin import TelegramSettingInline
    ...
    class CustomUserAdmin(UserAdmin):
        ...
        inlines = [TelegramSettingInline]
        # or add it to an existing entry
    ```

5. Configure the telegram settings. Refer to the documentation for all possible settings. 
Minimal configuration is like this:
    ```python
    # project/settings.py
    ...
    TELEGRAM = {
        "BOT_URL": "https://api.telegram.org/bot123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11/"
    }
    ...
    ```

6. Run `python manage.py migrate` to create the models.

7. Run `python manage.py setwebhook` to set the url on which you would like to receive telegram updates.

8. Start the development server and visit the admin to edit users and add/complete TelegramSettings there.

## License

This project is licensed under the MIT License — see the [`LICENSE`](https://github.com/shifqu/django-telegram-app/blob/main/LICENSE) file for details.