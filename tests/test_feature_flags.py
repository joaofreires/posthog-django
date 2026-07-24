from __future__ import annotations

from django.core.cache import caches

import posthog_django.feature_flags as feature_flags


class FakeClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []

    def get_feature_flag(self, key: str, distinct_id: str, **kwargs):
        self.calls.append((key, {"distinct_id": distinct_id, **kwargs}))
        return "variant-a"


def test_feature_flag_cache_hit(settings, monkeypatch):
    settings.POSTHOG_FEATURE_FLAGS_CACHE_TTL = 60

    client = FakeClient()
    monkeypatch.setattr(feature_flags, "get_client", lambda: client)
    monkeypatch.setattr(feature_flags, "_flag_cache", None)
    monkeypatch.setattr(feature_flags, "_flag_cache_key", None)

    caches["default"].clear()

    value1 = feature_flags.get_feature_flag(
        "flag-a", distinct_id="user-1", send_feature_flag_events=False
    )
    value2 = feature_flags.get_feature_flag(
        "flag-a", distinct_id="user-1", send_feature_flag_events=False
    )

    assert value1 == value2 == "variant-a"
    assert len(client.calls) == 1


def test_feature_flag_cache_skipped_when_sending_events(settings, monkeypatch):
    settings.POSTHOG_FEATURE_FLAGS_CACHE_TTL = 60

    client = FakeClient()
    monkeypatch.setattr(feature_flags, "get_client", lambda: client)
    monkeypatch.setattr(feature_flags, "_flag_cache", None)
    monkeypatch.setattr(feature_flags, "_flag_cache_key", None)

    caches["default"].clear()

    value1 = feature_flags.get_feature_flag(
        "flag-a",
        distinct_id="user-1",
        send_feature_flag_events=True,
    )
    value2 = feature_flags.get_feature_flag(
        "flag-a",
        distinct_id="user-1",
        send_feature_flag_events=True,
    )

    assert value1 == value2 == "variant-a"
    assert len(client.calls) == 2


def test_feature_flags_can_be_disabled(settings, monkeypatch):
    settings.POSTHOG_ENABLE_FEATURE_FLAGS = False

    def fail_if_client_is_created():
        raise AssertionError("feature flag helpers should not create the SDK client")

    monkeypatch.setattr(feature_flags, "get_client", fail_if_client_is_created)

    assert feature_flags.feature_enabled("flag-a", distinct_id="user-1") is None
    assert feature_flags.get_feature_flag("flag-a", distinct_id="user-1") is None
    assert feature_flags.get_feature_flag_result("flag-a", distinct_id="user-1") is None
    assert feature_flags.get_feature_flag_payload("flag-a", distinct_id="user-1") is None
    assert feature_flags.get_all_flags(distinct_id="user-1") is None
    assert feature_flags.get_all_flags_and_payloads(distinct_id="user-1") is None
