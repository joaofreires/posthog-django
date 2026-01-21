from __future__ import annotations

from posthog_django.cache import DjangoCacheFlagDefinitionCacheProvider
from posthog_django.cache import FeatureFlagResultCache


def test_flag_definition_cache_provider_roundtrip():
    provider = DjangoCacheFlagDefinitionCacheProvider(
        cache_alias="default",
        cache_prefix="posthog:test_flags",
        cache_ttl=30,
        lock_ttl=5,
    )

    assert provider.should_fetch_flag_definitions() is True
    assert provider.should_fetch_flag_definitions() is False

    data = {
        "flags": [{"key": "flag-a"}],
        "group_type_mapping": {},
        "cohorts": {},
    }
    provider.on_flag_definitions_received(data)

    cached = provider.get_flag_definitions()
    assert cached == data

    provider.shutdown()


def test_feature_flag_result_cache_handles_none():
    cache = FeatureFlagResultCache(
        cache_alias="default",
        prefix="posthog:test_feature_flags",
        ttl=30,
    )

    key = cache.build_key("flag-a", "user-1")
    cache.set(key, None)

    found, value = cache.get(key)
    assert found is True
    assert value is None

    cache.set(key, "variant")
    found, value = cache.get(key)
    assert found is True
    assert value == "variant"
