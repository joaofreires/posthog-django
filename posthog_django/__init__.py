from __future__ import annotations

from .client import configure
from .client import get_client
from .client import is_enabled
from .client import reset_client
from .events import alias
from .events import capture
from .events import capture_exception
from .events import group_identify
from .events import identify
from .events import set
from .events import set_once
from .feature_flags import feature_enabled
from .feature_flags import get_all_flags
from .feature_flags import get_all_flags_and_payloads
from .feature_flags import get_feature_flag
from .feature_flags import get_feature_flag_payload
from .feature_flags import get_feature_flag_result
from .middleware import PosthogContextMiddleware
from .utils import get_distinct_id
from .utils import set_distinct_id


class DjangoPosthog:
    def capture(self, *args, **kwargs):
        return capture(*args, **kwargs)

    def identify(self, *args, **kwargs):
        return identify(*args, **kwargs)

    def alias(self, *args, **kwargs):
        return alias(*args, **kwargs)

    def set(self, *args, **kwargs):
        return set(*args, **kwargs)

    def set_once(self, *args, **kwargs):
        return set_once(*args, **kwargs)

    def group_identify(self, *args, **kwargs):
        return group_identify(*args, **kwargs)

    def capture_exception(self, *args, **kwargs):
        return capture_exception(*args, **kwargs)

    def feature_enabled(self, *args, **kwargs):
        return feature_enabled(*args, **kwargs)

    def get_feature_flag(self, *args, **kwargs):
        return get_feature_flag(*args, **kwargs)

    def get_feature_flag_result(self, *args, **kwargs):
        return get_feature_flag_result(*args, **kwargs)

    def get_feature_flag_payload(self, *args, **kwargs):
        return get_feature_flag_payload(*args, **kwargs)

    def get_all_flags(self, *args, **kwargs):
        return get_all_flags(*args, **kwargs)

    def get_all_flags_and_payloads(self, *args, **kwargs):
        return get_all_flags_and_payloads(*args, **kwargs)

    def client(self):
        return get_client()


posthog = DjangoPosthog()

__all__ = [
    "PosthogContextMiddleware",
    "alias",
    "capture",
    "capture_exception",
    "configure",
    "feature_enabled",
    "get_all_flags",
    "get_all_flags_and_payloads",
    "get_client",
    "get_distinct_id",
    "get_feature_flag",
    "get_feature_flag_payload",
    "get_feature_flag_result",
    "group_identify",
    "identify",
    "is_enabled",
    "posthog",
    "reset_client",
    "set",
    "set_distinct_id",
    "set_once",
]
