"""Minimal Django settings for running tests."""

SECRET_KEY = "test-secret"
DEBUG = True
USE_TZ = True
ROOT_URLCONF = "tests.testapps.urls"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_telegram_app",  # the app we are testing
    "tests.testapps.samplebot",  # tiny sample app
]

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Config your package reads (from README Quickstart)
TELEGRAM = {
    "BOT_URL": "https://api.telegram.org/bot123:abc/",
    "ROOT_URL": "telegram/",
    "WEBHOOK_URL": "webhook",
    "WEBHOOK_TOKEN": "test-webhook-token",
}
