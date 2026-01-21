from __future__ import annotations

from typing import Any

from posthog import contexts

from .client import get_client
from .conf import get_settings
from .utils import build_request_tags
from .utils import get_or_create_distinct_id
from .utils import get_request_groups
from .utils import resolve_user_details
from .utils import set_distinct_id


def _resolve_request_identity(request: Any | None) -> tuple[str | None, str | None]:
    if request is None:
        return None, None

    user = getattr(request, "user", None)
    return resolve_user_details(user, user_id_field=get_settings().user_id_field)


def capture(
    event: str,
    *,
    request: Any | None = None,
    distinct_id: str | None = None,
    properties: dict[str, Any] | None = None,
    groups: dict[str, Any] | None = None,
    timestamp: Any | None = None,
    uuid: str | None = None,
    send_feature_flags: bool | dict[str, Any] | None = None,
    disable_geoip: bool | None = None,
) -> str | None:
    client = get_client()
    if client is None:
        return None

    user_id, user_email = _resolve_request_identity(request)
    resolved_distinct_id = distinct_id
    if resolved_distinct_id is None and request is not None:
        resolved_distinct_id = get_or_create_distinct_id(request, user_id=user_id)

    if groups is None and request is not None:
        groups = get_request_groups(request)

    merged_properties = {}
    if request is not None:
        merged_properties.update(build_request_tags(request, user_email=user_email))
    if properties:
        merged_properties.update(properties)

    return client.capture(
        event,
        distinct_id=resolved_distinct_id,
        properties=merged_properties or None,
        timestamp=timestamp,
        uuid=uuid,
        groups=groups,
        send_feature_flags=send_feature_flags if send_feature_flags is not None else False,
        disable_geoip=disable_geoip,
    )


def identify(
    distinct_id: str,
    *,
    request: Any | None = None,
    properties: dict[str, Any] | None = None,
    set_once_properties: dict[str, Any] | None = None,
) -> None:
    if request is not None:
        set_distinct_id(request, distinct_id)
    contexts.identify_context(distinct_id)

    if properties:
        set(properties=properties, distinct_id=distinct_id)
    if set_once_properties:
        set_once(properties=set_once_properties, distinct_id=distinct_id)


def set(
    *,
    request: Any | None = None,
    distinct_id: str | None = None,
    properties: dict[str, Any] | None = None,
    timestamp: Any | None = None,
    uuid: str | None = None,
    disable_geoip: bool | None = None,
) -> str | None:
    client = get_client()
    if client is None:
        return None

    user_id, _ = _resolve_request_identity(request)
    resolved_distinct_id = distinct_id
    if resolved_distinct_id is None and request is not None:
        resolved_distinct_id = get_or_create_distinct_id(request, user_id=user_id)

    return client.set(
        distinct_id=resolved_distinct_id,
        properties=properties,
        timestamp=timestamp,
        uuid=uuid,
        disable_geoip=disable_geoip,
    )


def set_once(
    *,
    request: Any | None = None,
    distinct_id: str | None = None,
    properties: dict[str, Any] | None = None,
    timestamp: Any | None = None,
    uuid: str | None = None,
    disable_geoip: bool | None = None,
) -> str | None:
    client = get_client()
    if client is None:
        return None

    user_id, _ = _resolve_request_identity(request)
    resolved_distinct_id = distinct_id
    if resolved_distinct_id is None and request is not None:
        resolved_distinct_id = get_or_create_distinct_id(request, user_id=user_id)

    return client.set_once(
        distinct_id=resolved_distinct_id,
        properties=properties,
        timestamp=timestamp,
        uuid=uuid,
        disable_geoip=disable_geoip,
    )


def alias(
    *,
    previous_id: str,
    distinct_id: str | None = None,
    request: Any | None = None,
    timestamp: Any | None = None,
    uuid: str | None = None,
    disable_geoip: bool | None = None,
) -> str | None:
    client = get_client()
    if client is None:
        return None

    resolved_distinct_id = distinct_id
    if resolved_distinct_id is None and request is not None:
        resolved_distinct_id = get_or_create_distinct_id(request)

    return client.alias(
        previous_id=previous_id,
        distinct_id=resolved_distinct_id,
        timestamp=timestamp,
        uuid=uuid,
        disable_geoip=disable_geoip,
    )


def group_identify(
    group_type: str,
    group_key: str,
    *,
    properties: dict[str, Any] | None = None,
    timestamp: Any | None = None,
    uuid: str | None = None,
    disable_geoip: bool | None = None,
) -> str | None:
    client = get_client()
    if client is None:
        return None

    return client.group_identify(
        group_type,
        group_key,
        properties=properties,
        timestamp=timestamp,
        uuid=uuid,
        disable_geoip=disable_geoip,
    )


def capture_exception(
    exception: Exception,
    *,
    request: Any | None = None,
    distinct_id: str | None = None,
    properties: dict[str, Any] | None = None,
    send_feature_flags: bool | dict[str, Any] | None = None,
    disable_geoip: bool | None = None,
) -> str | None:
    client = get_client()
    if client is None:
        return None

    user_id, user_email = _resolve_request_identity(request)
    resolved_distinct_id = distinct_id
    if resolved_distinct_id is None and request is not None:
        resolved_distinct_id = get_or_create_distinct_id(request, user_id=user_id)

    merged_properties = {}
    if request is not None:
        merged_properties.update(build_request_tags(request, user_email=user_email))
    if properties:
        merged_properties.update(properties)

    return client.capture_exception(
        exception,
        distinct_id=resolved_distinct_id,
        properties=merged_properties or None,
        send_feature_flags=send_feature_flags if send_feature_flags is not None else False,
        disable_geoip=disable_geoip,
    )
