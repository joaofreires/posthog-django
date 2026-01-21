SECRET_KEY = "test-secret-key"
DEBUG = True
USE_TZ = True

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

MIDDLEWARE = []

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}
