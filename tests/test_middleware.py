from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

from posthog_django.middleware import PosthogContextMiddleware


class FakeClient:
    def capture_exception(self, exception):
        self.exception = exception


class DummyRequest:
    def __init__(self):
        self.headers = {
            "X-POSTHOG-DISTINCT-ID": "header-id",
            "X-POSTHOG-SESSION-ID": "session-1",
        }
        self.method = "GET"
        self.path = "/"
        self.session = {}

    def build_absolute_uri(self):
        return "https://example.com/"


def test_middleware_sets_request_attributes(monkeypatch):
    client = FakeClient()
    monkeypatch.setattr("posthog_django.middleware.get_client", lambda: client)

    request = DummyRequest()
    request.user = SimpleNamespace(pk=7, email="user@example.com", is_authenticated=True)

    middleware = PosthogContextMiddleware(lambda req: "ok")
    response = middleware(request)

    assert response == "ok"
    assert request.posthog_distinct_id == "header-id"
    assert request.posthog == client


def test_view_capture_is_disabled_by_default(monkeypatch):
    calls = []
    monkeypatch.setattr(
        "posthog_django.middleware.capture",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )

    response = SimpleNamespace(status_code=200)
    middleware = PosthogContextMiddleware(lambda request: response)

    assert middleware(DummyRequest()) is response
    assert calls == []


@pytest.mark.parametrize("status_code", [200, 302, 404, 500])
def test_middleware_captures_view_with_response_metadata(settings, monkeypatch, status_code):
    settings.POSTHOG_MW_CAPTURE_VIEWS = True
    settings.POSTHOG_MW_VIEW_EVENT_NAME = "django_view"
    calls = []
    monkeypatch.setattr(
        "posthog_django.middleware.capture",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )

    request = DummyRequest()
    request.resolver_match = SimpleNamespace(view_name="app:detail")
    response = SimpleNamespace(status_code=status_code)
    middleware = PosthogContextMiddleware(lambda req: response)

    assert middleware(request) is response
    assert calls == [
        (
            ("django_view",),
            {
                "request": request,
                "properties": {
                    "$response_status_code": status_code,
                    "$django_view_name": "app:detail",
                },
            },
        )
    ]


def test_middleware_captures_unnamed_view(settings, monkeypatch):
    settings.POSTHOG_MW_CAPTURE_VIEWS = True
    calls = []
    monkeypatch.setattr(
        "posthog_django.middleware.capture",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )

    request = DummyRequest()
    request.resolver_match = SimpleNamespace(view_name=None)
    response = SimpleNamespace(status_code=204)
    middleware = PosthogContextMiddleware(lambda req: response)

    middleware(request)

    assert calls[0][0] == ("$pageview",)
    assert calls[0][1]["properties"] == {"$response_status_code": 204}


def test_request_filter_suppresses_view_capture(settings, monkeypatch):
    settings.POSTHOG_MW_CAPTURE_VIEWS = True
    settings.POSTHOG_MW_REQUEST_FILTER = lambda request: False
    calls = []
    monkeypatch.setattr(
        "posthog_django.middleware.capture",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )

    response = SimpleNamespace(status_code=200)
    middleware = PosthogContextMiddleware(lambda request: response)

    assert middleware(DummyRequest()) is response
    assert calls == []


def test_async_middleware_captures_view(settings, monkeypatch):
    settings.POSTHOG_MW_CAPTURE_VIEWS = True
    calls = []
    monkeypatch.setattr(
        "posthog_django.middleware.capture",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )

    response = SimpleNamespace(status_code=201)

    async def get_response(request):
        return response

    request = DummyRequest()
    middleware = PosthogContextMiddleware(get_response)

    assert asyncio.run(middleware(request)) is response
    assert calls[0][0] == ("$pageview",)
    assert calls[0][1]["request"] is request
    assert calls[0][1]["properties"] == {"$response_status_code": 201}
