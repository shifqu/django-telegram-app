"""Tests for admin.py."""

from unittest.mock import MagicMock

from django.contrib.admin.options import InlineModelAdmin
from django.test import SimpleTestCase

from django_telegram_app.admin import TelegramSettingInline


class AdminTests(SimpleTestCase):
    """Tests for django_telegram_app admin module."""

    def test_inline_is_subclass(self):
        """Test that TelegramSettingInline is a subclass of InlineModelAdmin."""
        assert issubclass(TelegramSettingInline, InlineModelAdmin)

    def test_callbackdata_admin_permissions(self):
        """Test that CallbackDataAdmin permissions are set correctly."""
        from django.contrib.admin.sites import AdminSite

        from django_telegram_app.admin import CallbackDataAdmin
        from django_telegram_app.models import CallbackData

        admin_instance = CallbackDataAdmin(CallbackData, AdminSite("test site"))
        request = MagicMock()  # Mock request object

        assert not admin_instance.has_add_permission(request)
        assert not admin_instance.has_delete_permission(request)
        assert not admin_instance.has_change_permission(request)

    def test_message_admin_permissions(self):
        """Test that MessageAdmin permissions are set correctly."""
        from django.contrib.admin.sites import AdminSite

        from django_telegram_app.admin import MessageAdmin
        from django_telegram_app.models import Message

        admin_instance = MessageAdmin(Message, AdminSite("test site"))
        request = MagicMock()  # Mock request object

        assert not admin_instance.has_add_permission(request)
        assert not admin_instance.has_delete_permission(request)
        assert not admin_instance.has_change_permission(request)
