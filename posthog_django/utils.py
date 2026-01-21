from __future__ import annotations

import uuid
from typing import Any

from .conf import get_settings


def resolve_user_details(user: Any, *, user_id_field: str) -> tuple[str | None, str | None]:
    user_id = None
    email = None

    if user is None:
        return user_id, email

    try:
        is_authenticated = getattr(user, "is_authenticated", False)
        if callable(is_authenticated):
            is_authenticated = is_authenticated()
    except Exception:
        return user_id, email

    if not is_authenticated:
        return user_id, email

    try:
        user_pk = getattr(user, user_id_field, None)
        if user_pk is not None:
            user_id = str(user_pk)

        user_email = getattr(user, "email", None)
        if user_email:
            email = str(user_email)
    except Exception:
        return user_id, email

    return user_id, email


def get_request_header(request: Any, name: str) -> str | None:
    headers = getattr(request, "headers", None)
    if headers is not None:
        return headers.get(name)

    meta_key = f"HTTP_{name.upper().replace('-', '_')}"
    meta = getattr(request, "META", {})
    return meta.get(meta_key)


def get_request_ip(request: Any, header_name: str) -> str | None:
    value = get_request_header(request, header_name)
    if value:
        return value.split(",")[0].strip()

    meta = getattr(request, "META", {})
    return meta.get("REMOTE_ADDR")


def get_distinct_id(
    request: Any,
    *,
    user_id: str | None = None,
) -> str | None:
    config = get_settings()

    distinct_id = getattr(request, "posthog_distinct_id", None)
    if distinct_id:
        return str(distinct_id)

    header_value = get_request_header(request, config.distinct_id_header)
    if header_value:
        return str(header_value)

    if user_id:
        return str(user_id)

    if config.store_distinct_id_in_session and hasattr(request, "session"):
        session_value = request.session.get(config.session_distinct_id_key)
        if session_value:
            return str(session_value)

    return None


def get_or_create_distinct_id(
    request: Any,
    *,
    user_id: str | None = None,
) -> str | None:
    config = get_settings()
    distinct_id = get_distinct_id(request, user_id=user_id)
    if distinct_id:
        return distinct_id

    if config.store_distinct_id_in_session and hasattr(request, "session"):
        distinct_id = str(uuid.uuid4())
        request.session[config.session_distinct_id_key] = distinct_id
        request.posthog_distinct_id = distinct_id
        return distinct_id

    return None


def set_distinct_id(request: Any, distinct_id: str) -> None:
    config = get_settings()
    request.posthog_distinct_id = distinct_id
    if config.store_distinct_id_in_session and hasattr(request, "session"):
        request.session[config.session_distinct_id_key] = distinct_id


def build_request_tags(
    request: Any,
    *,
    user_email: str | None = None,
) -> dict[str, Any]:
    config = get_settings()
    tags: dict[str, Any] = {}

    if user_email:
        tags["email"] = user_email

    absolute_url = getattr(request, "build_absolute_uri", None)
    if callable(absolute_url):
        url = absolute_url()
        if url:
            tags["$current_url"] = url

    if getattr(request, "method", None):
        tags["$request_method"] = request.method

    if getattr(request, "path", None):
        tags["$request_path"] = request.path

    ip_address = get_request_ip(request, config.request_ip_header)
    if ip_address:
        tags["$ip_address"] = ip_address

    user_agent = get_request_header(request, "User-Agent")
    if user_agent:
        tags["$user_agent"] = user_agent

    if config.request_extra_tags:
        extra = config.request_extra_tags(request)
        if extra:
            tags.update(extra)

    if config.request_tag_map:
        mapped = config.request_tag_map(tags)
        if mapped is not None:
            tags = mapped

    return tags


def get_request_groups(request: Any) -> dict[str, Any]:
    groups = getattr(request, "posthog_groups", None)
    if isinstance(groups, dict):
        return groups

    resolver = getattr(request, "posthog_groups_resolver", None)
    if callable(resolver):
        return resolver()

    config = get_settings()
    if config.groups_resolver:
        return config.groups_resolver(request)

    return {}
