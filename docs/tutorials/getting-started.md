# 🚀 Getting Started

This tutorial will guide you through installing **django-telegram-app**, configuring your project, and verifying that your Telegram bot is connected and ready to receive commands.

By the end of this page, you will have:

- installed `django-telegram-app`
- added the required configuration
- set up the webhook
- successfully received your first update from Telegram

This assumes you already:

- [created a Django project](https://docs.djangoproject.com/en/5.2/intro/tutorial01/){: target="_blank"}
- [created a superuser](https://docs.djangoproject.com/en/5.2/ref/django-admin/#createsuperuser){: target="_blank"}

---

## 1. Install the library

Install the package using pip:

```text
pip install django-telegram-app
```

---

## 2. Add to Django’s installed apps

In your project’s `settings.py`, add:

```python title="mysite/settings.py"
INSTALLED_APPS = [
    ...
    "django_telegram_app",
]
```

---

## 3. Configure the TELEGRAM settings

Create a bot using Telegram’s [**@BotFather**](https://t.me/botfather), then add this to your Django settings:

```python title="mysite/settings.py, minimum settings"
TELEGRAM = {
    "BOT_URL": "https://api.telegram.org/bot<your-bot-token>/",  # replace with your bot token
}
```

See the [configuration reference](../reference/configuration.md) for available settings.

---

## 4. Add the webhook route

In your project’s `urls.py`:

```python title="mysite/urls.py"
from django.urls import path, include
from django_telegram_app.conf import settings as telegram_settings

urlpatterns = [
    ...
    path(telegram_settings.ROOT_URL, include("django_telegram_app.urls")),
]
```

This exposes the webhook endpoint under:

```text
/telegram/webhook/
```

---

## 5. Apply migrations

The library includes a few models (settings + callback tokens + messages). Run:

```text
python manage.py migrate
```

---

## 6. Register your webhook

!!! note
    During early development, you may not have a public domain or HTTPS endpoint available.  
    In this case, we recommend using an HTTP tunneling service.  
    Lightweight options such as [pinggy](https://pinggy.io/) or [localhost.run](https://localhost.run/) work well for quick testing, while [ngrok](https://ngrok.com/) provides a more complete feature set, including stable URLs and request inspection.  

Run the management command:

```text
python manage.py setwebhook <base-url>
```

If successful, you’ll see:

```text
Successfully set webhook to "..."
```

Telegram will now deliver all messages sent to your bot to your Django server.  

---

## Start your server
During development this is as simple as running:
```text
python manage.py runserver
```

!!! warning "Invalid HTTP_HOST header"
    If you encounter an error like:

    ```
    Invalid HTTP_HOST header: '<your-tunnel-url>'.
    ```

    This is normal when using tunneling services. Add your tunnel domain to
    `ALLOWED_HOSTS` or use:

    ```python
    ALLOWED_HOSTS = ["*"]
    ```

---

## 7. Link your Telegram chat to a `TelegramSettings` entry

Before your bot can respond to any command, you must associate your Telegram chat with a `TelegramSettings` instance.
**django-telegram-app** does not auto-create settings for new chats unless you explicitly enable the setting [ALLOW_SETTINGS_CREATION_FROM_UPDATES](../reference/configuration.md/#allow_settings_creation_from_updates).

### Option A — Manually obtain your chat ID and create a TelegramSettings entry
1. Message [@userinfobot](https://telegram.me/userinfobot). It will reply with your chat_id.
2. Open the Django admin and log in.
3. Navigate to:  
    Telegram settings → Add Telegram settings  
    or use the direct url:  
    `<yourdomain>/admin/django_telegram_app/telegramsettings/add/`
4. Create a new TelegramSettings entry using the chat ID you retrieved.  
    This links your Telegram chat to your Django bot instance.

### Option B — Temporarily enable automatic creation
If you prefer not to manually look up your chat ID:  
1. In your Django settings, enable:
```python title="mysite/settings.py"
TELEGRAM = {
    ...
    "ALLOW_SETTINGS_CREATION_FROM_UPDATES": True,
}
```
2. Restart your server.  
3. Continue to the next step and send /start to your bot, your TelegramSettings entry will be created automatically.

You may disable the setting again afterward if you do not want auto-creation in production.

---

## 8. Test your setup

Open a chat with your Telegram-bot and send:
```text
/start
```
You should now find a message in the admin under  
> `DJANGO_TELEGRAM_APP > Messages`

Once you see updates appearing there, your bot is fully connected and ready for use.

!!! note
    At this point, your bot will reply with the default help message.
    This is expected — you have not created any commands yet.
    In the next tutorial, you will add your first real bot command.
---

## Next steps

Continue to:

**[👉 Writing Your First Command](dice-roller-tutorial.md)**