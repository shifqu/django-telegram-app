---
title: ""
hide:
  - title
---
<h1 align="center">
Django Telegram App
</h1>
<p align="center">
  <img src="assets/logo.png" alt="django-telegram-app logo" width="480">
</p>
<p align="center">
<i>A Django app to integrate Telegram bots into your project.</i>
</p>
<div align="center">
<hr/>
<a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/badge/style-ruff-8b5000" alt="Style: ruff"/></a>
<a href="https://github.com/RobertCraigie/pyright-python"><img src="https://img.shields.io/badge/typing-pyright-725a42" alt="Typing: pyright"/></a>
<a href="https://github.com/pylint-dev/pylint"><img src="https://img.shields.io/badge/linting-pylint-755147" alt="Linting: pylint"/></a>
<a href="https://docs.djangoproject.com/en/5.2/"><img src="https://img.shields.io/badge/framework-django-727242" alt="Framework: Django" /></a>
<a href="https://opensource.org/license/mit"><img src="https://img.shields.io/github/license/mashape/apistatus.svg" alt="License" /></a>
<a href="https://github.com/shifqu/django-telegram-app/actions/workflows/ci.yml"><img src="https://github.com/shifqu/django-telegram-app/actions/workflows/ci.yml/badge.svg" alt="CI Validation" /></a>
<hr/>

</div>

## Features

- ✅ Command-based bot architecture with step-based flow
- ✅ Swappable `TelegramSettings` model
- ✅ Optional admin integration for Telegram settings
- ✅ Extensible: add commands per app via auto-discovery
- ✅ Built-in system checks for misconfiguration
- ✅ Django ORM integration (no direct API handling required)
- ✅ Easy to test (includes custom TelegramTestCase)

## Requirements

- Python **3.10+**
- Django **5.2+**

## Quick start

1. Install the package
        
        pip install django-telegram-app

1. Add "django_telegram_app" to your INSTALLED_APPS setting like this:
    
        INSTALLED_APPS = [
            ...,
            "django_telegram_app",
        ]

2. Include the telegram URLconf in your project urls.py like this:

        ...
        from django_telegram_app.conf import settings as telegram_app_settings
        ...
        path(telegram_app_settings.ROOT_URL, include("django_telegram_app.urls")),

3. Create your own commands in each app under `{appname}/telegrambot/commands/`. Refer to the documentation for more details on how to write custom commands.

5. Configure the telegram settings. Refer to the documentation for all possible settings. 
Minimal configuration is like this:

        # mysite/settings.py
        ...
        TELEGRAM = {
            "BOT_URL": "https://api.telegram.org/bot123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11/"
        }
        ...

6. Run `python manage.py migrate` to create the models.

7. Run `python manage.py setwebhook` to set the url on which you would like to receive telegram updates.

8. Start the development server and visit the admin to edit/add TelegramSettings there.

## License

This project is licensed under the MIT License — see the [`LICENSE`](https://github.com/shifqu/django-telegram-app/blob/main/LICENSE) file for details.