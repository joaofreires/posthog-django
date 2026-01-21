from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from django.conf import settings

DEFAULT_HOST = "https://app.posthog.com"


@dataclass(frozen=True)
class PosthogSettings:
    project_api_key: str | None
    host: str | None
    enabled: bool
    debug: bool
    send: bool
    sync_mode: bool
    disabled: bool
    personal_api_key: str | None
    poll_interval: int
    disable_geoip: bool
    feature_flags_request_timeout_seconds: int
    super_properties: dict[str, Any] | None
    enable_exception_autocapture: bool
    log_captured_exceptions: bool
    project_root: str | None
    privacy_mode: bool
    enable_local_evaluation: bool
    cache_alias: str
    flag_definitions_cache_ttl: int
    flag_definitions_lock_ttl: int
    flag_definitions_cache_prefix: str
    feature_flags_cache_ttl: int
    feature_flags_cache_prefix: str
    distinct_id_header: str
    session_id_header: str
    request_ip_header: str
    request_tag_map: Callable[[dict[str, Any]], dict[str, Any]] | None
    request_extra_tags: Callable[[Any], dict[str, Any]] | None
    request_filter: Callable[[Any], bool] | None
    capture_exceptions: bool
    user_id_field: str
    session_distinct_id_key: str
    store_distinct_id_in_session: bool
    groups_resolver: Callable[[Any], dict[str, Any]] | None


def _get_setting(name: str, default: Any) -> Any:
    return getattr(settings, name, default)


def get_settings() -> PosthogSettings:
    project_api_key = _get_setting("POSTHOG_PROJECT_API_KEY", None) or _get_setting(
        "POSTHOG_API_KEY", None
    )

    enabled = _get_setting("POSTHOG_ENABLED", project_api_key is not None)
    disabled = _get_setting("POSTHOG_DISABLED", False) or not enabled

    poll_interval = int(_get_setting("POSTHOG_POLL_INTERVAL", 30))

    flag_definitions_cache_ttl = int(
        _get_setting("POSTHOG_FLAG_DEFINITIONS_CACHE_TTL", max(60, poll_interval * 2))
    )
    flag_definitions_lock_ttl = int(
        _get_setting("POSTHOG_FLAG_DEFINITIONS_LOCK_TTL", max(5, poll_interval))
    )

    request_tag_map = _get_setting("POSTHOG_MW_TAG_MAP", None)
    if not callable(request_tag_map):
        request_tag_map = None

    request_extra_tags = _get_setting("POSTHOG_MW_EXTRA_TAGS", None)
    if not callable(request_extra_tags):
        request_extra_tags = None

    request_filter = _get_setting("POSTHOG_MW_REQUEST_FILTER", None)
    if not callable(request_filter):
        request_filter = None

    capture_exceptions = _get_setting("POSTHOG_MW_CAPTURE_EXCEPTIONS", True)

    groups_resolver = _get_setting("POSTHOG_GROUPS_RESOLVER", None)
    if not callable(groups_resolver):
        groups_resolver = None

    return PosthogSettings(
        project_api_key=project_api_key,
        host=_get_setting("POSTHOG_HOST", None),
        enabled=enabled,
        debug=_get_setting("POSTHOG_DEBUG", False),
        send=_get_setting("POSTHOG_SEND", True),
        sync_mode=_get_setting("POSTHOG_SYNC_MODE", False),
        disabled=disabled,
        personal_api_key=_get_setting("POSTHOG_PERSONAL_API_KEY", None),
        poll_interval=poll_interval,
        disable_geoip=_get_setting("POSTHOG_DISABLE_GEOIP", True),
        feature_flags_request_timeout_seconds=int(
            _get_setting("POSTHOG_FEATURE_FLAGS_REQUEST_TIMEOUT_SECONDS", 3)
        ),
        super_properties=_get_setting("POSTHOG_SUPER_PROPERTIES", None),
        enable_exception_autocapture=_get_setting("POSTHOG_ENABLE_EXCEPTION_AUTOCAPTURE", False),
        log_captured_exceptions=_get_setting("POSTHOG_LOG_CAPTURED_EXCEPTIONS", False),
        project_root=_get_setting("POSTHOG_PROJECT_ROOT", None),
        privacy_mode=_get_setting("POSTHOG_PRIVACY_MODE", False),
        enable_local_evaluation=_get_setting("POSTHOG_ENABLE_LOCAL_EVALUATION", True),
        cache_alias=_get_setting("POSTHOG_CACHE_ALIAS", "default"),
        flag_definitions_cache_ttl=flag_definitions_cache_ttl,
        flag_definitions_lock_ttl=flag_definitions_lock_ttl,
        flag_definitions_cache_prefix=_get_setting(
            "POSTHOG_FLAG_DEFINITIONS_CACHE_PREFIX", "posthog:flag_definitions"
        ),
        feature_flags_cache_ttl=int(_get_setting("POSTHOG_FEATURE_FLAGS_CACHE_TTL", 0)),
        feature_flags_cache_prefix=_get_setting(
            "POSTHOG_FEATURE_FLAGS_CACHE_PREFIX", "posthog:feature_flags"
        ),
        distinct_id_header=_get_setting("POSTHOG_DISTINCT_ID_HEADER", "X-POSTHOG-DISTINCT-ID"),
        session_id_header=_get_setting("POSTHOG_SESSION_ID_HEADER", "X-POSTHOG-SESSION-ID"),
        request_ip_header=_get_setting("POSTHOG_REQUEST_IP_HEADER", "X-Forwarded-For"),
        request_tag_map=request_tag_map,
        request_extra_tags=request_extra_tags,
        request_filter=request_filter,
        capture_exceptions=bool(capture_exceptions),
        user_id_field=_get_setting("POSTHOG_USER_ID_FIELD", "pk"),
        session_distinct_id_key=_get_setting(
            "POSTHOG_SESSION_DISTINCT_ID_KEY", "posthog_distinct_id"
        ),
        store_distinct_id_in_session=_get_setting("POSTHOG_STORE_DISTINCT_ID_IN_SESSION", True),
        groups_resolver=groups_resolver,
    )
