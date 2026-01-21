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


def _handle_error(mode: str, error: Exception | str | None) -> None:
    if mode == "ignore":
        return

    message = error if isinstance(error, str) else repr(error)

    if mode == "raise":
        if isinstance(error, Exception):
            raise error
        raise RuntimeError(message)

    logger.warning("PostHog error: %s", message)


def _resolve_on_error(mode: str):
    if mode == "ignore":
        return None

    def on_error(error, *args, **kwargs) -> None:  # noqa: ANN001
        _handle_error(mode, error)

    return on_error


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
        on_error=_resolve_on_error(config.on_error_mode),
        poll_interval=config.poll_interval,
        disabled=config.disabled,
        disable_geoip=config.disable_geoip,
        feature_flags_request_timeout_seconds=config.feature_flags_request_timeout_seconds,
        super_properties=config.super_properties,
        enable_exception_autocapture=config.enable_exception_autocapture,
        capture_exception_code_variables=config.capture_exception_code_variables,
        code_variables_mask_patterns=config.code_variables_mask_patterns,
        code_variables_ignore_patterns=config.code_variables_ignore_patterns,
        in_app_modules=config.in_app_modules,
        log_captured_exceptions=config.log_captured_exceptions,
        project_root=config.project_root,
        privacy_mode=config.privacy_mode,
        enable_local_evaluation=config.enable_local_evaluation,
        flag_definition_cache_provider=cache_provider,
    )
    return client


def validate_client() -> bool:
    config = get_settings()
    if not config.validate_on_startup:
        return True

    if not config.project_api_key:
        logger.warning("PostHog validation skipped: API key is missing.")
        return False

    if not config.enabled or config.disabled:
        logger.info("PostHog validation skipped: integration is disabled.")
        return False

    error_state: dict[str, Exception | str | None] = {"error": None}
    base_handler = _resolve_on_error(config.on_error_mode)

    def on_error(error, *args, **kwargs) -> None:  # noqa: ANN001
        error_state["error"] = error or "Unknown PostHog error"
        if base_handler is not None:
            base_handler(error, *args, **kwargs)

    client = Client(
        config.project_api_key,
        host=config.host,
        debug=config.debug,
        send=True,
        sync_mode=True,
        personal_api_key=config.personal_api_key,
        on_error=on_error,
        poll_interval=config.poll_interval,
        disabled=config.disabled,
        disable_geoip=config.disable_geoip,
        feature_flags_request_timeout_seconds=config.feature_flags_request_timeout_seconds,
        super_properties=config.super_properties,
        enable_exception_autocapture=False,
        capture_exception_code_variables=config.capture_exception_code_variables,
        code_variables_mask_patterns=config.code_variables_mask_patterns,
        code_variables_ignore_patterns=config.code_variables_ignore_patterns,
        in_app_modules=config.in_app_modules,
        log_captured_exceptions=config.log_captured_exceptions,
        project_root=config.project_root,
        privacy_mode=config.privacy_mode,
        enable_local_evaluation=config.enable_local_evaluation,
    )

    message_id = client.capture(
        config.validate_event_name,
        distinct_id=config.validate_distinct_id,
        properties={"$source": "posthog_django"},
    )
    client.shutdown()

    if error_state["error"] or message_id is None:
        error = error_state["error"] or "Validation event did not enqueue"
        _handle_error(config.on_error_mode, error)
        return False

    logger.info("PostHog validation succeeded.")
    return True


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
