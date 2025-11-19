# ⚙️ Configuring the Telegram bot

All configuration for **django-telegram-app** is provided inside a single TELEGRAM dictionary in your Django settings.
Only one setting (`TELEGRAM_SETTINGS_MODEL`) is defined outside this dictionary, as required by Django’s swappable-model system.
```python
# settings.py
TELEGRAM = {
    "BOT_URL": "...",  # required
    "ROOT_URL": "telegram/",
    ...
}

TELEGRAM_SETTINGS_MODEL = "django_telegram_app.TelegramSettings"  # This is the default and can be omitted.
```


## Configuration reference
| Setting                       | Required | Default                                      | Example                                                                    | Description                                                                                                                                                                                 |
| ----------------------------- | -------- | -------------------------------------------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`BOT_URL`**                 | ✅ Yes    | —                                            | `"https://api.telegram.org/bot123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11/"` | The full URL to your Telegram bot, including the bot token. Used for all outbound requests to the Telegram Bot API.                                                                         |
| **`ROOT_URL`**                | ❌ No     | `"telegram/"`                                | `"bot/"`                                                                   | The root URL prefix under which all Telegram-related views are registered. Used in your project's `urls.py` and by the `setwebhook` command to construct the webhook endpoint.              |
| **`WEBHOOK_URL`**             | ❌ No     | `"webhook"`                                  | `"secret-hook-XYZ/"`                                                       | The final segment of the webhook URL path. Customize to make the webhook endpoint less predictable to external callers.                                                                     |
| **`WEBHOOK_TOKEN`**           | ❌ No     | `""`                                         | `"s3cr3t-t0ken-1234"`                                                      | Secret token that Telegram must include in the `X-Telegram-Bot-Api-Secret-Token` header when sending updates to your webhook. If empty, no token is expected or configured by `setwebhook`. |
| **`ALLOW_SETTINGS_CREATION_FROM_UPDATES`**     | ❌ No     | `False` | `True`                                                   | Whether or not to allow TelegramSettings to be created when handling updates.                                                                                        |
| **`REGISTER_DEFAULT_ADMIN`**     | ❌ No     | `True` | `False`                                                   | Whether or not to register the default model admin.                                                                                        |
| **`TELEGRAM_SETTINGS_MODEL`** | ❌ No     | `"django_telegram_app.TelegramSettings"`            | `"myapp.CustomTelegramSettings"`                                           | Path to your swappable `TelegramSettings` model. Must subclass `AbstractTelegramSettings`.                                                                                                  |

## Example configuration
```python
# settings.py
TELEGRAM = {
    "BOT_URL": "https://api.telegram.org/bot123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11/",
    "ROOT_URL": "telegram/",
    "WEBHOOK_URL": "supersecret/",
    "WEBHOOK_TOKEN": "my-telegram-webhook-secret",
    "ALLOW_SETTINGS_CREATION_FROM_UPDATES": False,
    "REGISTER_DEFAULT_ADMIN": True,
}

TELEGRAM_SETTINGS_MODEL = "django_telegram_app.TelegramSettings"
```
Then include the Telegram URLs in your project’s root urls.py:
```python
from django_telegram_app.conf import settings as telegram_app_settings

urlpatterns = [
    path(telegram_app_settings.ROOT_URL, include("django_telegram_app.urls")),
]
```
