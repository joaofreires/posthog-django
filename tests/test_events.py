from __future__ import annotations

from types import SimpleNamespace

import posthog_django.events as events


class FakeClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []

    def capture(self, event: str, **kwargs):
        self.calls.append((event, kwargs))
        return "event-id"

    def set(self, **kwargs):
        self.calls.append(("set", kwargs))
        return "set-id"

    def set_once(self, **kwargs):
        self.calls.append(("set_once", kwargs))
        return "set-once-id"

    def alias(self, **kwargs):
        self.calls.append(("alias", kwargs))
        return "alias-id"

    def group_identify(self, *args, **kwargs):
        self.calls.append(("group_identify", {"args": args, **kwargs}))
        return "group-id"

    def capture_exception(self, exception, **kwargs):
        self.calls.append(("capture_exception", {"exception": exception, **kwargs}))
        return "exception-id"


class DummyRequest:
    def __init__(self):
        self.headers = {
            "User-Agent": "pytest",
            "X-Forwarded-For": "10.0.0.1, 10.0.0.2",
        }
        self.method = "GET"
        self.path = "/test"
        self.session = {}
        self.posthog_groups = {"company": "acme"}

    def build_absolute_uri(self):
        return "https://example.com/test"


def test_capture_builds_properties(monkeypatch):
    client = FakeClient()
    monkeypatch.setattr(events, "get_client", lambda: client)

    user = SimpleNamespace(pk=123, email="user@example.com", is_authenticated=True)
    request = DummyRequest()
    request.user = user

    result = events.capture(
        "user_signed_up",
        request=request,
        properties={"plan": "pro"},
    )

    assert result == "event-id"
    assert client.calls
    event_name, payload = client.calls[0]
    assert event_name == "user_signed_up"
    assert payload["distinct_id"] == "123"
    assert payload["groups"] == {"company": "acme"}

    properties = payload["properties"]
    assert properties["plan"] == "pro"
    assert properties["email"] == "user@example.com"
    assert properties["$current_url"] == "https://example.com/test"
    assert properties["$request_method"] == "GET"
    assert properties["$request_path"] == "/test"
    assert properties["$ip_address"] == "10.0.0.1"
    assert properties["$user_agent"] == "pytest"


def test_identify_sets_distinct_id(monkeypatch):
    client = FakeClient()
    monkeypatch.setattr(events, "get_client", lambda: client)

    request = DummyRequest()
    events.identify("abc", request=request, properties={"role": "admin"})

    assert request.posthog_distinct_id == "abc"
    assert any(call[0] == "set" for call in client.calls)
