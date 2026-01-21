from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from typing import Any

from posthog import contexts

from .client import get_client
from .conf import get_settings
from .utils import build_request_tags
from .utils import get_or_create_distinct_id
from .utils import get_request_header
from .utils import resolve_user_details

try:
    from asgiref.sync import iscoroutinefunction
    from asgiref.sync import markcoroutinefunction
except ImportError:  # pragma: no cover - legacy fallback
    import asyncio

    iscoroutinefunction = asyncio.iscoroutinefunction

    def markcoroutinefunction(func: Callable[..., Any]) -> Callable[..., Any]:
        return func


class PosthogContextMiddleware:
    sync_capable = True
    async_capable = True

    def __init__(self, get_response: Callable[[Any], Any]) -> None:
        self.get_response = get_response
        self._is_coroutine = iscoroutinefunction(get_response)

        if self._is_coroutine:
            markcoroutinefunction(self)

        config = get_settings()
        self.request_filter = config.request_filter
        self.capture_exceptions = config.capture_exceptions
        self.session_header = config.session_id_header
        self.client = get_client()
        self.user_id_field = config.user_id_field

    def _apply_context(self, request: Any, *, user_id: str | None, user_email: str | None) -> None:
        session_id = get_request_header(request, self.session_header)
        if session_id:
            contexts.set_context_session(session_id)

        distinct_id = get_or_create_distinct_id(request, user_id=user_id)
        if distinct_id:
            contexts.identify_context(distinct_id)
            request.posthog_distinct_id = distinct_id

        tags = build_request_tags(request, user_email=user_email)
        for key, value in tags.items():
            contexts.tag(key, value)

        if self.client is not None:
            request.posthog = self.client

    def __call__(self, request: Any) -> Any | Awaitable[Any]:
        if self._is_coroutine:
            return self.__acall__(request)

        if self.request_filter and not self.request_filter(request):
            return self.get_response(request)

        user = getattr(request, "user", None)
        user_id, user_email = resolve_user_details(user, user_id_field=self.user_id_field)

        with contexts.new_context(
            fresh=True,
            capture_exceptions=self.capture_exceptions,
            client=self.client,
        ):
            self._apply_context(request, user_id=user_id, user_email=user_email)
            return self.get_response(request)

    async def __acall__(self, request: Any) -> Any:
        if self.request_filter and not self.request_filter(request):
            return await self.get_response(request)

        user_id: str | None = None
        user_email: str | None = None
        auser = getattr(request, "auser", None)
        if callable(auser):
            try:
                user = await auser()
                user_id, user_email = resolve_user_details(user, user_id_field=self.user_id_field)
            except Exception:
                user_id, user_email = None, None

        with contexts.new_context(
            fresh=True,
            capture_exceptions=self.capture_exceptions,
            client=self.client,
        ):
            self._apply_context(request, user_id=user_id, user_email=user_email)
            return await self.get_response(request)

    def process_exception(self, request: Any, exception: Exception) -> None:
        if self.request_filter and not self.request_filter(request):
            return

        if not self.capture_exceptions:
            return

        client = self.client or get_client()
        if client is not None:
            client.capture_exception(exception)
