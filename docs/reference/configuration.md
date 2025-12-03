# 🛠 Configuring the Telegram bot

All configuration for **django-telegram-app** is provided inside a single `TELEGRAM` dictionary in your Django settings.
Only one setting (`TELEGRAM_SETTINGS_MODEL`) is defined outside this dictionary, as required by Django’s swappable-model system.

---

## Required Settings
Here’s a list of required settings.

### BOT_URL

The full URL to your Telegram bot, including the bot token. Used for all outbound requests to the Telegram Bot API. Example:

```python title="mysite/settings.py"
TELEGRAM = {
    "BOT_URL": "https://api.telegram.org/bot123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11/"
}
```

---

## Optional Settings
Here’s a list of optional settings and their default values.

### ROOT_URL
Default: `"telegram/"`

The root URL prefix under which all Telegram-related views are registered. Used in your project's `urls.py` and by the `setwebhook` and `setcommands` commands to construct the webhook endpoint. Example:

```python title="mysite/settings.py"
TELEGRAM = {
    "ROOT_URL": "bot/"
}
```

### WEBHOOK_URL
Default: `"webhook"`

The final segment of the webhook URL path. Customize to make the webhook endpoint less predictable to malicious users. Example:

```python title="mysite/settings.py"
TELEGRAM = {
    "WEBHOOK_URL": "secret-hook-XYZ"
}
```

### WEBHOOK_TOKEN
Default: `""` (empty string)

Secret token that Telegram must include in the `X-Telegram-Bot-Api-Secret-Token` header when sending updates to your webhook. If empty, no token is expected or configured by `setwebhook`. Example:

```python title="mysite/settings.py"
TELEGRAM = {
    "WEBHOOK_TOKEN": "s3cr3t-t0ken-1234"
}
```

### ALLOW_SETTINGS_CREATION_FROM_UPDATES
Default: `False` (bool)

Allow the app to automatically create a TelegramSettings entry when a new chat contacts the bot. Example:

```python title="mysite/settings.py"
TELEGRAM = {
    "ALLOW_SETTINGS_CREATION_FROM_UPDATES": True
}
```

### REGISTER_DEFAULT_ADMIN
Default: `True` (bool)

Controls whether the default Django admin for the TelegramSettings model is automatically registered. Example:

```python title="mysite/settings.py"
TELEGRAM = {
    "REGISTER_DEFAULT_ADMIN": False
}
```

### HELP_TEXT_INTRO
Default: `"Currently available commands:"`

A short paragraph placed **before** the auto-generated command list in the `help` message.

This setting only controls the introductory text.
The list of commands is still generated automatically from the discovered `Command` objects (excluding any marked with `exclude_from_help=True`).
You should not include command listings yourself.

A blank line is automatically inserted between the intro and the generated command list, so you may omit a trailing newline unless you want additional spacing.

```python title="mysite/settings.py"
TELEGRAM= {
    ...
    "HELP_TEXT_INTRO": "Hi, I am a bot with a custom intro!\nI can do the following for you:",
}
```

### HELP_TEXT_RENDERER
Default: `None`

Provides full control over the help message that django_telegram_app sends when unexpected or unrecognized input is received.

Set this to a dotted path string pointing to a callable.
If this setting is defined, it replaces the entire help message, including the command list.
In this case, HELP_TEXT_INTRO is ignored.  
Use this setting when you want complete control over the presentation of help text, formatting, structure, or command layout, rather than relying on the app’s default auto-generated command list.

```python
def custom_help_renderer(telegram_settings: "AbstractTelegramSettings") -> str:
    ...
```
It must return the full help message as a string.

```python title="mysite/settings.py"
TELEGRAM= {
    ...
    "HELP_TEXT_RENDERER": "myapp.telegram.custom_help_renderer",
}
```

### TELEGRAM_SETTINGS_MODEL
Default: "django_telegram_app.TelegramSettings"

Path to your swappable `TelegramSettings` model. Must subclass `AbstractTelegramSettings`. Example:

```python title="mysite/settings.py"
TELEGRAM_SETTINGS_MODEL = "myapp.CustomTelegramSettings"
```

!!! note
    This is a root setting and should **not** be included in the TELEGRAM dict.

---

## Full example configuration
```python title="mysite/settings.py"
TELEGRAM = {
    "BOT_URL": "https://api.telegram.org/bot123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11/",
    "ROOT_URL": "bot/",
    "WEBHOOK_URL": "secret-hook-XYZ",
    "WEBHOOK_TOKEN": "s3cr3t-t0ken-1234",
    "ALLOW_SETTINGS_CREATION_FROM_UPDATES": True,
    "REGISTER_DEFAULT_ADMIN": False,
    "HELP_TEXT_INTRO": "Hi, I am a bot with a custom intro!\nI can do the following for you:",
}

TELEGRAM_SETTINGS_MODEL = "myapp.TelegramSettings"
```

---

## Accessing settings in your project

Inside your own project code, keep using Django’s standard settings object:

```python title="mysite/settings.py"
from django.conf import settings

if settings.DEBUG:
    ...
```

**django-telegram-app** only reads:

```python title="mysite/settings.py"
TELEGRAM
TELEGRAM_SETTINGS_MODEL
```

It does not replace or wrap django.conf.settings for general Django
configuration. Should you require telegram specific settings (in `mysite/urls.py` for example), you can use the provided settings object.

```python title="mysite/settings.py"
from django_telegram_app.conf import settings as telegram_settings

print(telegram_settings.BOT_URL)
```