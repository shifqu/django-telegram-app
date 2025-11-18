"""Telegram admin."""

from django.contrib import admin

from django_telegram_app import get_telegram_settings_model
from django_telegram_app.conf import settings
from django_telegram_app.models import CallbackData, Message

TelegramSettingModel = get_telegram_settings_model()


class TelegramSettingInline(admin.TabularInline):
    """Represent a telegram setting inline in the admin."""

    model = TelegramSettingModel


class TelegramSettingsAdmin(admin.ModelAdmin):
    """Represent the TelegramSettings admin."""


class CallbackDataAdmin(admin.ModelAdmin):
    """Represent the CallbackData admin."""

    list_display = ("token", "data_truncated")

    def has_add_permission(self, request):  # noqa: ARG002  # pylint: disable=unused-argument
        """Do not allow to add callback_data."""
        return False

    def has_delete_permission(self, request, obj=None):  # noqa: ARG002  # pylint: disable=unused-argument
        """Do not allow to delete callback_data."""
        return False

    def has_change_permission(self, request, obj=None):  # noqa: ARG002  # pylint: disable=unused-argument
        """Do not allow to change callback_data."""
        return False


class MessageAdmin(admin.ModelAdmin):
    """Represent the Message admin."""

    list_display = ("update_id", "message_truncated", "error")

    def has_add_permission(self, request):  # noqa: ARG002  # pylint: disable=unused-argument
        """Do not allow to add messages."""
        return False

    def has_delete_permission(self, request, obj=None):  # noqa: ARG002  # pylint: disable=unused-argument
        """Do not allow to delete messages."""
        return False

    def has_change_permission(self, request, obj=None):  # noqa: ARG002  # pylint: disable=unused-argument
        """Do not allow to change messages."""
        return False


admin.site.register(CallbackData, CallbackDataAdmin)
admin.site.register(Message, MessageAdmin)
if settings.REGISTER_DEFAULT_ADMIN:
    admin.site.register(TelegramSettingModel, TelegramSettingsAdmin)
