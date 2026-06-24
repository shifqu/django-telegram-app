# 🎛 Callback Data

**Callback data** powers multi-step interactions in `django-telegram-app`.

Instead of storing JSON or long strings in Telegram callback buttons,
the library stores structured data in the `CallbackData` model and inserts a short token into the button.

## Why this approach?

- Telegram limits callback data to 64 bytes  
- Many commands need to pass structured data (ids, choices, state markers)
- Storing in DB avoids encoding/decoding issues
- Database entries are automatically cleaned up when a command finishes

---

## Creating callback data

Steps expose several helpers that each create a `CallbackData` entry and return a token string for use in an inline button:

| Method | Routes to |
|---|---|
| `self.next_step_callback(**kwargs)` | the next step in the command |
| `self.previous_step_callback(steps_back=N, **kwargs)` | N steps back |
| `self.current_step_callback(**kwargs)` | the same step again (reload) |
| `self.cancel_callback(**kwargs)` | cancels the command |
| `self.callback_to(step, **kwargs)` | any specific step by name, instance, or class |

`callback_to()` is the most flexible option — use it when you need to jump to an arbitrary step rather than following the linear order:

```python
token = self.callback_to("StepName", some_value=123)
# or pass the step class (only works when exactly one instance of that class is registered):
token = self.callback_to(SomeStep, some_value=123)
```

All helpers:
1. Create a `CallbackData` object in the database
2. Store your provided kwargs alongside a `correlation_key`
3. Return a short token string to use in the inline button

---

## Retrieving callback data

When a user taps a button:

```python
data = self.get_callback_data(update)
```

This:
- resolves the token
- returns the stored dict

---

## How `callback_to()` and `go_to()` relate

When a user taps a button whose token was created with `callback_to()`, the dispatcher calls `BaseBotCommand.go_to(step_name, telegram_update)` on the command instance. You can also call `go_to()` directly from within a step or command when you want to redirect to a specific step without waiting for a button press:

```python
return self.command.go_to("StepName", telegram_update)
```

`go_to()` raises `ValueError` if the step name is not registered on the command.

---

## Default Callback Data

If a step is triggered without callback data (e.g. first step),  
the framework injects:

```python
{"correlation_key": "<uuid>"}
```

The correlation key links all callback data for the same command execution.

---

Callback data is central to building multi-step flows with correct context and minimal payload size.
