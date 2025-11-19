"""Tests for admin.py."""

import importlib
from unittest.mock import MagicMock, patch

from django.contrib.admin.options import InlineModelAdmin
from django.test import SimpleTestCase

from django_telegram_app import admin


class AdminTests(SimpleTestCase):
    """Tests for django_telegram_app admin module."""

    def test_inline_is_subclass(self):
        """Test that TelegramSettingInline is a subclass of InlineModelAdmin."""
        assert issubclass(admin.TelegramSettingInline, InlineModelAdmin)

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

    def test_telegramsettings_admin_not_registered(self):
        """Test that TelegramSettingsAdmin is not registered if the setting REGISTER_DEFAULT_ADMIN is False."""
        from django.contrib.admin.sites import site

        from django_telegram_app.conf import settings

        site._registry.clear()
        with patch.object(settings, "REGISTER_DEFAULT_ADMIN", False):
            importlib.reload(admin)

            assert "TelegramSettings" not in [model.__name__ for model in site._registry.keys()]
