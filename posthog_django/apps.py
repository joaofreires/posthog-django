from __future__ import annotations

from django.apps import AppConfig


class PosthogDjangoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "posthog_django"

    def ready(self) -> None:
        from .client import configure

        configure()
