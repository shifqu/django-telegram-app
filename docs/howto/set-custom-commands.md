# 📋 Add custom commands to your bot's command list

Telegram provides a built‑in menu that lets users invoke commands
without typing them manually.  
This menu appears when users tap the command button or begin typing `/`.

------------------------------------------------------------------------

## Set your commands in Telegram

Use the management command:

``` bash
python manage.py setcommands
```

If successful, you'll see:

``` text
Successfully called setMyCommands
```

Telegram will now display your custom commands---along with their
descriptions---in the bot's menu.

------------------------------------------------------------------------

## Set commands for different languages

Telegram allows commands and their descriptions to be localized per
language code.

### Make descriptions translatable

Use Django's translation framework (`gettext`, `gettext_lazy`) and
provide translations in your `.po` files.  
See the Django documentation for details on [internationalization](https://docs.djangoproject.com/en/5.2/topics/i18n/).

### Re-run the command with locales

``` bash
python manage.py setcommands --locale=nl --locale=en
```

This sets translated commands for each specified locale.

------------------------------------------------------------------------

## Delete all commands from the list

To clear the command list entirely:

``` bash
python.manage.py setcommands --delete
```

If successful:

``` text
Successfully called deleteMyCommands
```

------------------------------------------------------------------------

## Include commands normally excluded from help

Commands marked with `exclude_from_help=True` are not included by
default.

Use `--include-hidden` to include them:

``` bash
python manage.py setcommands --include-hidden
```

You typically won't use this option, but it's available for the rare
cases where hidden commands should still appear in Telegram's menu.
