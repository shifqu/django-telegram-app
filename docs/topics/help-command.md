# Help Command Behavior

`django_telegram_app` automatically sends a **help message** whenever
input is received that is not expected or understood.

After having completed the tutorial, the help message would be:
```text
Currently available commands:
/roll - Roll a D&D-style die (d4, d6, d8, d10, d12, d20).
```

## Intro Text

You can customize the introductory paragraph of this help message using
the Django setting:

```python title="mysite/settings.py"
TELEGRAM = {
    ...
    "HELP_TEXT_INTRO": "Hi! I am a custom intro!",
}
```

This text appears *before* the auto‑generated command list.  
A blank line is automatically inserted after the intro.

## Auto‑Generated Command List

The command list is generated from the autodiscovered `Command`
classes.  
Each entry uses:
```text
/<name> - <description>
```

### Excluding Commands

To hide a command from the help output, set `exclude_from_help` on your `Command` subclass:

```python title="myapp/telegrambot/commands/concrete.py"
class Command(BaseBotCommand):
    ...
    exclude_from_help = True
    ...
```

## Full Customization with HELP_TEXT_RENDERER

If you want complete control over the help message---including the
command list---you can provide a custom renderer.

Set:

```python title="mysite/settings.py"
TELEGRAM = {
    ...
    "HELP_TEXT_RENDERER": "path.to.my_help_renderer"
}
```

This must be a **dotted path to a callable** with the signature:

``` python
def my_help_renderer(telegram_settings: "AbstractTelegramSettings") -> str:
    ...
```

If `HELP_TEXT_RENDERER` is set, `HELP_TEXT_INTRO` is ignored entirely.
