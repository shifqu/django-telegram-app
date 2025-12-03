# 🛠️ How-To Guides

The **How-To Guides** provide short, focused instructions for accomplishing
specific tasks with **django-telegram-app**.  
These guides are **goal-oriented** rather than conceptual—they show you *how to do something* without requiring deep knowledge of the framework's internals.

Use these when you have a concrete task in mind and want a clear set of steps to follow.

---

## Available How-To Guides

### Swap `TelegramSettings`
Learn how to replace the default `TelegramSettings` model with your own implementation, add custom fields, and enable full typing support.

👉 See: [`swap-telegramsettings.md`](swap-telegramsettings.md)

---

### Write Management Commands
Create management commands that interact with your bot using the provided `BaseManagementCommand` foundation.

👉 See: [`write-management-commands.md`](write-management-commands.md)

---

### Debug Bot Issues
Practical steps to diagnose problems such as missing updates, callback errors, webhook misconfiguration, or stale persisted state.

👉 See: [`debug-bot-issues.md`](debug-bot-issues.md)

---

### Set custom commands in your bot’s command list

Learn how to configure or update the commands that appear in Telegram’s built-in command menu for your bot.

👉 See: [`set-custom-commands.md`](set-custom-commands.md)

---

## When to use these guides

Use a how-to guide when:

- You want to complete a *specific technical task*
- You don’t need background theory or API details
- You prefer a short, example-driven explanation
- You’ve completed the tutorials and want to extend your bot

If you need deeper architecture explanations instead, refer to the [Topic Guides](../topics/index.md), and if you need detailed API documentation, see the [Reference](../reference/index.md) section.

Happy building! 🚀
