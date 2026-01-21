import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "replace-me"
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "posthog_django",
    "example_app",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "posthog_django.middleware.PosthogContextMiddleware",
]

ROOT_URLCONF = "example_project.urls"

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
    }
]

WSGI_APPLICATION = "example_project.wsgi.application"
ASGI_APPLICATION = "example_project.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# PostHog configuration
POSTHOG_PROJECT_API_KEY = os.getenv("POSTHOG_PROJECT_API_KEY", "phc_your_project_key")
POSTHOG_PERSONAL_API_KEY = os.getenv("POSTHOG_PERSONAL_API_KEY", "phx_your_personal_key")
POSTHOG_HOST = os.getenv("POSTHOG_HOST", "https://app.posthog.com")
POSTHOG_FEATURE_FLAGS_CACHE_TTL = 60
POSTHOG_ERROR_MODE = os.getenv("POSTHOG_ERROR_MODE", "log")
POSTHOG_VALIDATE_ON_STARTUP = os.getenv("POSTHOG_VALIDATE_ON_STARTUP", "true").lower() == "true"
POSTHOG_ENABLE_EXCEPTION_AUTOCAPTURE = (
    os.getenv("POSTHOG_ENABLE_EXCEPTION_AUTOCAPTURE", "true").lower() == "true"
)
POSTHOG_CAPTURE_EXCEPTION_CODE_VARIABLES = (
    os.getenv("POSTHOG_CAPTURE_EXCEPTION_CODE_VARIABLES", "true").lower() == "true"
)
POSTHOG_CODE_VARIABLES_MASK_PATTERNS = [
    r"(?i).*password.*",
    r"(?i).*token.*",
]
POSTHOG_CODE_VARIABLES_IGNORE_PATTERNS = [
    r"^__.*",
]
