# 🔧 Using a Custom TelegramSettings Model

By default, the library ships with its own `TelegramSettings` model.
If your project needs additional fields (for example, `user`, `reminder_text`, preferences or feature flags), you can replace it entirely with your own model.

## Why use a custom TelegramSettings model instead of creating a completely separate model?
Because the library is designed to treat TelegramSettings as the source of all Telegram-related configuration. When you swap the model instead of creating a separate one, you get several important advantages:

- **Automatic availability in commands and steps**  
    The TelegramSettings instance is loaded once when a command is instantiated.
    Every command automatically receives it as `self.settings` and every step receives the command as `self.command`, so your custom fields are available everywhere with no extra code.
- **No repeated queries or imports**  
    With a separate model, you would have to:
    - import it in every command and step
    - manually fetch it (`MyExtraSettings.objects.get(...)`)
    - handle missing records or defaults yourself.

    *Swapping eliminates all of that boilerplate.*

- **Cleaner, single source of truth**  
    All Telegram-related settings —default ones and your custom ones— live in one model tied directly to the commands.
- **Automatically integrated into the Django admin**  
The library registers `TelegramSettings` as a `ModelAdmin` in Django-admin.  
When you swap the model, your custom version automatically appears there too, making it easy to edit all Telegram settings in one place without extra admin configuration.
To disable registering this `ModelAdmin`, set the option `REGISTER_DEFAULT_ADMIN` to `False`
- **Inline admin integrations to link to other models**
An Inline is also provided to enable users to link and modify telegram settings to another model.
Add the provided telegramsettings inline to another model like this:
```python title="myapp/admin.py"
from django_telegram_app.admin import TelegramSettingInline


class MyAppAdmin(ModelAdmin):
    inlines = [TelegramSettingInline] # or add it to an existing entry

```

---

## Create the custom model
- Subclass django_telegram_app.AbstractTelegramSettings and add any fields your bot needs (e.g., extra_field).
```python title="apps/myapp/models.py"
from django.db import models

from django_telegram_app.models import AbstractTelegramSettings


class CustomTelegramSettings(AbstractTelegramSettings):
    extra_field = models.CharField(max_length=100, default="")
```
- Point Django to your model via the TELEGRAM_SETTINGS_MODEL setting.
```python title="mysite/settings.py"
TELEGRAM_SETTINGS_MODEL = "myapp.TelegramSettings"
```
- Run migrations as usual.
```text
python manage.py makemigrations
python manage.py migrate
```
After these steps, the library will automatically use your model whenever it loads Telegram settings.

---

## Adding Typing Support for Your Custom Model

Django’s model-swapping works seamlessly at runtime, but type checkers only know about the abstract base class unless you tell them otherwise.
To enable full typing support—autocomplete, type checking, and access to your custom fields—you can define a simple *project-local* base class for your Telegram commands.

This keeps your application code clean and avoids having to repeat type hints or generics in every command.

Below is an example pattern you can copy into your project:
```python title="apps/myapp/telegrambot/base.py"
from abc import ABC

from django_telegram_app.bot.base import BaseBotCommand, Step

from myapp.models import TelegramSettings


class TelegramCommand(BaseBotCommand, ABC):
    """Project specific base class for telegram commands."""

    settings: TelegramSettings


class TelegramStep(Step, ABC):
    """Project specific base class for telegram command steps."""

    command: TelegramCommand

```
!!! note "Why the ABC?"
    `BaseBotCommand` and `Step` contain abstract methods that subclasses must implement
    (e.g., .handle() or .steps). By inheriting from `ABC`, we are explicitly marking these project-local bases as **abstract**, meaning:
    - they should not be instantiated directly
    - `Pylint`/`mypy`/`IDE tools` will not complain about missing abstract methods,

---

## Result
With this setup:
```python title="myapp/telegrambot/commands/concrete.py"
class Command(TelegramCommand):
    ...

class ExampleStep(TelegramStep):
    def handle(self, update):
        text = self.command.settings.extra_field  # fully typed!
        ...
```
- `self.command.settings` is recognized as your custom TelegramSettings
- all custom fields and methods autocomplete correctly
- no generics, no casts, no boilerplate per command

Clean library, clean project, excellent typing.