from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from django.core.cache import caches
from posthog.flag_definition_cache import FlagDefinitionCacheData
from posthog.flag_definition_cache import FlagDefinitionCacheProvider


class DjangoCacheFlagDefinitionCacheProvider(FlagDefinitionCacheProvider):
    def __init__(
        self,
        *,
        cache_alias: str,
        cache_prefix: str,
        cache_ttl: int,
        lock_ttl: int,
    ) -> None:
        self.cache = caches[cache_alias]
        self.cache_key = f"{cache_prefix}:data"
        self.lock_key = f"{cache_prefix}:lock"
        self.cache_ttl = cache_ttl
        self.lock_ttl = lock_ttl

    def get_flag_definitions(self) -> FlagDefinitionCacheData | None:
        return self.cache.get(self.cache_key)

    def should_fetch_flag_definitions(self) -> bool:
        return bool(self.cache.add(self.lock_key, "1", timeout=self.lock_ttl))

    def on_flag_definitions_received(self, data: FlagDefinitionCacheData) -> None:
        self.cache.set(self.cache_key, data, timeout=self.cache_ttl)
        self.cache.delete(self.lock_key)

    def shutdown(self) -> None:
        self.cache.delete(self.lock_key)


@dataclass(frozen=True)
class FeatureFlagCacheKey:
    key: str
    distinct_id: str
    context_hash: str


class FeatureFlagResultCache:
    _none_sentinel = "__posthog_none__"

    def __init__(self, *, cache_alias: str, prefix: str, ttl: int) -> None:
        self.cache = caches[cache_alias]
        self.prefix = prefix
        self.ttl = ttl

    def build_key(
        self,
        key: str,
        distinct_id: str,
        *,
        groups: dict[str, Any] | None = None,
        person_properties: dict[str, Any] | None = None,
        group_properties: dict[str, Any] | None = None,
        only_evaluate_locally: bool = False,
        device_id: str | None = None,
    ) -> FeatureFlagCacheKey:
        payload = {
            "groups": groups or {},
            "person_properties": person_properties or {},
            "group_properties": group_properties or {},
            "only_evaluate_locally": only_evaluate_locally,
            "device_id": device_id,
        }
        encoded = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
        digest = hashlib.sha256(encoded).hexdigest()
        return FeatureFlagCacheKey(
            key=key,
            distinct_id=distinct_id,
            context_hash=digest,
        )

    def _format_cache_key(self, key: FeatureFlagCacheKey) -> str:
        return f"{self.prefix}:{key.key}:{key.distinct_id}:{key.context_hash}"

    def get(self, key: FeatureFlagCacheKey) -> tuple[bool, Any | None]:
        cached = self.cache.get(self._format_cache_key(key))
        if cached is None:
            return False, None
        if cached == self._none_sentinel:
            return True, None
        return True, cached

    def set(self, key: FeatureFlagCacheKey, value: Any | None) -> None:
        payload = self._none_sentinel if value is None else value
        self.cache.set(self._format_cache_key(key), payload, timeout=self.ttl)
