from __future__ import annotations

import logging
import threading

from django.conf import settings as django_settings
from posthog import Client

from .cache import DjangoCacheFlagDefinitionCacheProvider
from .conf import get_settings

logger = logging.getLogger(__name__)

_client: Client | None = None
_client_lock = threading.Lock()


def is_enabled() -> bool:
    config = get_settings()
    return bool(config.project_api_key) and config.enabled and not config.disabled


def _build_client() -> Client | None:
    config = get_settings()
    if not config.project_api_key:
        logger.warning("PostHog project API key missing; events are disabled.")
        return None

    if not config.enabled or config.disabled:
        return None

    cache_provider = None
    if config.flag_definitions_cache_ttl > 0:
        cache_provider = DjangoCacheFlagDefinitionCacheProvider(
            cache_alias=config.cache_alias,
            cache_prefix=config.flag_definitions_cache_prefix,
            cache_ttl=config.flag_definitions_cache_ttl,
            lock_ttl=config.flag_definitions_lock_ttl,
        )

    client = Client(
        config.project_api_key,
        host=config.host,
        debug=config.debug,
        send=config.send,
        sync_mode=config.sync_mode,
        personal_api_key=config.personal_api_key,
        poll_interval=config.poll_interval,
        disabled=config.disabled,
        disable_geoip=config.disable_geoip,
        feature_flags_request_timeout_seconds=config.feature_flags_request_timeout_seconds,
        super_properties=config.super_properties,
        enable_exception_autocapture=config.enable_exception_autocapture,
        log_captured_exceptions=config.log_captured_exceptions,
        project_root=config.project_root,
        privacy_mode=config.privacy_mode,
        enable_local_evaluation=config.enable_local_evaluation,
        flag_definition_cache_provider=cache_provider,
    )
    return client


def get_client() -> Client | None:
    global _client

    override_client = getattr(django_settings, "POSTHOG_CLIENT", None)
    if isinstance(override_client, Client):
        return override_client

    if _client is None:
        with _client_lock:
            if _client is None:
                _client = _build_client()
    return _client


def configure(client: Client | None = None) -> None:
    global _client
    if client is not None:
        _client = client
        return

    _client = _build_client()


def reset_client() -> None:
    global _client
    if _client is not None:
        try:
            _client.shutdown()
        except Exception:
            logger.exception("Failed to shutdown PostHog client cleanly.")
        _client = None
