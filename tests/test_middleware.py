from __future__ import annotations

from types import SimpleNamespace

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
