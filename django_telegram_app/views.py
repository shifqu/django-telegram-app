"""Telegram views."""

import json
import logging

from django.contrib.auth.decorators import login_not_required  # type: ignore[reportAttributeAccessIssue]
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from django_telegram_app import models
from django_telegram_app.bot import bot


@csrf_exempt
@login_not_required
def webhook(request: HttpRequest):
    """Handle incoming messages."""
    if not bot.is_valid_token(request.headers.get("X-Telegram-Bot-Api-Secret-Token")):
        return JsonResponse({"status": "error", "message": "Invalid token."}, status=403)
    update = json.loads(request.body)
    message = models.Message(raw_message=update)
    status = "ok"
    try:
        bot.handle_update(update)
    except Exception as exc:
        message.error = str(exc)
        status = "error"
        logging.exception("Error handling Telegram update")
    finally:
        message.save()
    return JsonResponse({"status": status, "message": "Message received."})
