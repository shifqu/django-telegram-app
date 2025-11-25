# 🎲 Extending Your First Command

This tutorial starts where [dice roller](dice-roller-tutorial.md) left off. You’ll extend the **D&D-style dice roller** by making the bot ask for who the roll will happen. This demonstrates the *waiting for user input* principle.

By the end, your bot will:

- respond to `/roll`
- ask for who the roll is being made
- let the user choose a die (`d4`, `d6`, `d8`, `d10`, `d12`, `d20`)
- display the result
- offer a “Roll again”, "Choose another die" and "Roll for another player" button

This assumes you already:

- implemented the `/roll` command

---

## 1. Update the steps property of the command

Create `dice/telegrambot/commands/roll.py`:

```diff title="dice/telegrambot/commands/roll.py"
class Command(BaseBotCommand):
    ...
    @property
    def steps(self):
        """Return the steps of the command."""
-       return [ChooseDie(self), ShowResult(self)]
+       return [AskName(self), ChooseDie(self), ShowResult(self)]
```

---

## 2. Update the ShowResult step
```diff  title="dice/telegrambot/commands/roll.py"
class ShowResult(Step):
    ...
    def handle(self, update: TelegramUpdate):
        ...
        sides = int(data["sides"])
+       character_name = data["character_name"]
        ...
        previous_step_callback = self.previous_step_callback(steps_back=1, original_data=data)
+       two_steps_back_callback = self.previous_step_callback(steps_back=2, original_data=data)
        keyboard = [
            [{"text": "🔁 Roll again", "callback_data": self.current_step_callback(data)}],
            [{"text": "🎯 Choose another die", "callback_data": previous_step_callback}],
+           [{"text": "✏️ Choose another name", "callback_data": two_steps_back_callback}],
        ]
        ...
        bot.send_message(
-           f"You rolled *{result}* on a d{sides}! 🎉",
+           f"{character_name} rolled *{result}* on a d{sides}! 🎉",
            self.command.settings.chat_id,
            reply_markup={"inline_keyboard": keyboard},
            message_id=update.message_id,
        )

```

---

## 3. Implement the new step
```python  title="dice/telegrambot/commands/roll.py"
class AskName(Step):
    """Ask the user for their character's name."""

    def handle(self, telegram_update: TelegramUpdate):
        """Prompt the user to enter their character name."""
        self.add_waiting_for("character_name")
        bot.send_message(
            "What's your character's name?",
            self.command.settings.chat_id,
            message_id=telegram_update.message_id,
        )

```

This command stores the waiting_for state on the chat's telegram-settings. On the next message sent by the user to the bot, the input will be used to fill the key `character_name` in the callbackdata.

---

## Next steps

Continue to:

**[👉 Write tests for your command](write-tests.md)**