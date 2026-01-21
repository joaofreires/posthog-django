from __future__ import annotations

from typing import Any

from posthog.types import FeatureFlagResult

from .cache import FeatureFlagResultCache
from .client import get_client
from .conf import get_settings
from .utils import get_or_create_distinct_id
from .utils import get_request_groups
from .utils import resolve_user_details

_flag_cache: FeatureFlagResultCache | None = None
_flag_cache_key: tuple[str, int, str] | None = None


def _get_flag_cache() -> FeatureFlagResultCache | None:
    global _flag_cache
    global _flag_cache_key

    config = get_settings()
    if config.feature_flags_cache_ttl <= 0:
        return None

    cache_key = (
        config.cache_alias,
        config.feature_flags_cache_ttl,
        config.feature_flags_cache_prefix,
    )
    if _flag_cache is None or _flag_cache_key != cache_key:
        _flag_cache = FeatureFlagResultCache(
            cache_alias=config.cache_alias,
            prefix=config.feature_flags_cache_prefix,
            ttl=config.feature_flags_cache_ttl,
        )
        _flag_cache_key = cache_key

    return _flag_cache


def _resolve_distinct_id(*, request: Any | None, distinct_id: str | None) -> str | None:
    if distinct_id:
        return distinct_id
    if request is None:
        return None
    user = getattr(request, "user", None)
    user_id = None
    if user is not None:
        user_id, _ = resolve_user_details(user, user_id_field=get_settings().user_id_field)
    return get_or_create_distinct_id(request, user_id=user_id)


def feature_enabled(
    key: str,
    *,
    request: Any | None = None,
    distinct_id: str | None = None,
    groups: dict[str, Any] | None = None,
    person_properties: dict[str, Any] | None = None,
    group_properties: dict[str, Any] | None = None,
    only_evaluate_locally: bool = False,
    send_feature_flag_events: bool = True,
    disable_geoip: bool | None = None,
    device_id: str | None = None,
    use_cache: bool = True,
) -> bool | None:
    variant = get_feature_flag(
        key,
        request=request,
        distinct_id=distinct_id,
        groups=groups,
        person_properties=person_properties,
        group_properties=group_properties,
        only_evaluate_locally=only_evaluate_locally,
        send_feature_flag_events=send_feature_flag_events,
        disable_geoip=disable_geoip,
        device_id=device_id,
        use_cache=use_cache,
    )
    if variant is None:
        return None
    return bool(variant)


def get_feature_flag_result(
    key: str,
    *,
    request: Any | None = None,
    distinct_id: str | None = None,
    groups: dict[str, Any] | None = None,
    person_properties: dict[str, Any] | None = None,
    group_properties: dict[str, Any] | None = None,
    only_evaluate_locally: bool = False,
    send_feature_flag_events: bool = True,
    disable_geoip: bool | None = None,
    device_id: str | None = None,
) -> FeatureFlagResult | None:
    client = get_client()
    if client is None:
        return None

    resolved_distinct_id = _resolve_distinct_id(request=request, distinct_id=distinct_id)
    if resolved_distinct_id is None:
        return None

    if groups is None and request is not None:
        groups = get_request_groups(request)

    return client.get_feature_flag_result(
        key,
        resolved_distinct_id,
        groups=groups,
        person_properties=person_properties,
        group_properties=group_properties,
        only_evaluate_locally=only_evaluate_locally,
        send_feature_flag_events=send_feature_flag_events,
        disable_geoip=disable_geoip,
        device_id=device_id,
    )


def get_feature_flag(
    key: str,
    *,
    request: Any | None = None,
    distinct_id: str | None = None,
    groups: dict[str, Any] | None = None,
    person_properties: dict[str, Any] | None = None,
    group_properties: dict[str, Any] | None = None,
    only_evaluate_locally: bool = False,
    send_feature_flag_events: bool = True,
    disable_geoip: bool | None = None,
    device_id: str | None = None,
    use_cache: bool = True,
) -> Any | None:
    client = get_client()
    if client is None:
        return None

    resolved_distinct_id = _resolve_distinct_id(request=request, distinct_id=distinct_id)
    if resolved_distinct_id is None:
        return None

    if groups is None and request is not None:
        groups = get_request_groups(request)

    cache = _get_flag_cache() if use_cache and not send_feature_flag_events else None
    if cache is not None:
        cache_key = cache.build_key(
            key,
            resolved_distinct_id,
            groups=groups,
            person_properties=person_properties,
            group_properties=group_properties,
            only_evaluate_locally=only_evaluate_locally,
            device_id=device_id,
        )
        found, cached_value = cache.get(cache_key)
        if found:
            return cached_value

    value = client.get_feature_flag(
        key,
        resolved_distinct_id,
        groups=groups,
        person_properties=person_properties,
        group_properties=group_properties,
        only_evaluate_locally=only_evaluate_locally,
        send_feature_flag_events=send_feature_flag_events,
        disable_geoip=disable_geoip,
        device_id=device_id,
    )

    if cache is not None:
        cache.set(cache_key, value)

    return value


def get_feature_flag_payload(
    key: str,
    *,
    request: Any | None = None,
    distinct_id: str | None = None,
    match_value: Any | None = None,
    groups: dict[str, Any] | None = None,
    person_properties: dict[str, Any] | None = None,
    group_properties: dict[str, Any] | None = None,
    only_evaluate_locally: bool = False,
    send_feature_flag_events: bool = False,
    disable_geoip: bool | None = None,
    device_id: str | None = None,
) -> Any | None:
    client = get_client()
    if client is None:
        return None

    resolved_distinct_id = _resolve_distinct_id(request=request, distinct_id=distinct_id)
    if resolved_distinct_id is None:
        return None

    if groups is None and request is not None:
        groups = get_request_groups(request)

    return client.get_feature_flag_payload(
        key,
        resolved_distinct_id,
        match_value=match_value,
        groups=groups,
        person_properties=person_properties,
        group_properties=group_properties,
        only_evaluate_locally=only_evaluate_locally,
        send_feature_flag_events=send_feature_flag_events,
        disable_geoip=disable_geoip,
        device_id=device_id,
    )


def get_all_flags(
    *,
    request: Any | None = None,
    distinct_id: str | None = None,
    groups: dict[str, Any] | None = None,
    person_properties: dict[str, Any] | None = None,
    group_properties: dict[str, Any] | None = None,
    only_evaluate_locally: bool = False,
    disable_geoip: bool | None = None,
    device_id: str | None = None,
    flag_keys_to_evaluate: list[str] | None = None,
) -> dict[str, Any] | None:
    client = get_client()
    if client is None:
        return None

    resolved_distinct_id = _resolve_distinct_id(request=request, distinct_id=distinct_id)
    if resolved_distinct_id is None:
        return None

    if groups is None and request is not None:
        groups = get_request_groups(request)

    return client.get_all_flags(
        resolved_distinct_id,
        groups=groups,
        person_properties=person_properties,
        group_properties=group_properties,
        only_evaluate_locally=only_evaluate_locally,
        disable_geoip=disable_geoip,
        device_id=device_id,
        flag_keys_to_evaluate=flag_keys_to_evaluate,
    )


def get_all_flags_and_payloads(
    *,
    request: Any | None = None,
    distinct_id: str | None = None,
    groups: dict[str, Any] | None = None,
    person_properties: dict[str, Any] | None = None,
    group_properties: dict[str, Any] | None = None,
    only_evaluate_locally: bool = False,
    disable_geoip: bool | None = None,
    device_id: str | None = None,
    flag_keys_to_evaluate: list[str] | None = None,
) -> dict[str, Any] | None:
    client = get_client()
    if client is None:
        return None

    resolved_distinct_id = _resolve_distinct_id(request=request, distinct_id=distinct_id)
    if resolved_distinct_id is None:
        return None

    if groups is None and request is not None:
        groups = get_request_groups(request)

    return client.get_all_flags_and_payloads(
        resolved_distinct_id,
        groups=groups,
        person_properties=person_properties,
        group_properties=group_properties,
        only_evaluate_locally=only_evaluate_locally,
        disable_geoip=disable_geoip,
        device_id=device_id,
        flag_keys_to_evaluate=flag_keys_to_evaluate,
    )
