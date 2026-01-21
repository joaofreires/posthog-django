from __future__ import annotations

from django.apps import AppConfig


class PosthogDjangoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "posthog_django"

    def ready(self) -> None:
        from .client import configure, validate_client
        from .conf import get_settings

        configure()
        if get_settings().validate_on_startup:
            validate_client()
