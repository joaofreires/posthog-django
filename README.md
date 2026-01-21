# posthog-django

Django helpers for the PostHog Python SDK. This package provides a Django-ready
client, middleware, feature flag helpers, and a small sugar API.

## Install

```bash
pip install posthog-django
```

## Configure

Add the app and middleware, then set your API keys.

```python
# settings.py
INSTALLED_APPS = [
    # ...
    "posthog_django",
]

MIDDLEWARE = [
    # ...
    "posthog_django.middleware.PosthogContextMiddleware",
]

POSTHOG_PROJECT_API_KEY = "phc_your_project_key"
POSTHOG_PERSONAL_API_KEY = "phx_your_personal_key"  # required for local flag eval
POSTHOG_HOST = "https://app.posthog.com"  # optional
```

## Capture events

```python
from posthog_django import capture

def signup_view(request):
    # ...
    capture("user_signed_up", request=request, properties={"plan": "pro"})
```

## Feature flags

```python
from posthog_django import feature_enabled, get_feature_flag

def dashboard(request):
    if feature_enabled("new-dashboard", request=request):
        ...

    variant = get_feature_flag("pricing-experiment", request=request)
```

## Settings reference

- `POSTHOG_PROJECT_API_KEY` or `POSTHOG_API_KEY`: required.
- `POSTHOG_PERSONAL_API_KEY`: required for local feature flag evaluation.
- `POSTHOG_HOST`: PostHog host (default `https://app.posthog.com`).
- `POSTHOG_ENABLED`: enable/disable integration (default: enabled if API key is set).
- `POSTHOG_DEBUG`: enable SDK debug logging.
- `POSTHOG_DISABLE_GEOIP`: disable GeoIP lookup (default: True).
- `POSTHOG_ERROR_MODE`: `log`, `raise`, or `ignore` for SDK errors (default: `log`).
- `POSTHOG_MW_CAPTURE_EXCEPTIONS`: capture exceptions in middleware (default: True).
- `POSTHOG_MW_EXTRA_TAGS`: callable returning extra context tags.
- `POSTHOG_MW_REQUEST_FILTER`: callable returning False to skip tracking.
- `POSTHOG_MW_TAG_MAP`: callable to mutate tags before they are added.
- `POSTHOG_CACHE_ALIAS`: Django cache alias to use (default: "default").
- `POSTHOG_FLAG_DEFINITIONS_CACHE_TTL`: seconds to cache flag definitions.
- `POSTHOG_FLAG_DEFINITIONS_LOCK_TTL`: seconds for the flag definition lock.
- `POSTHOG_FLAG_DEFINITIONS_CACHE_PREFIX`: cache key prefix for flag definitions.
- `POSTHOG_FEATURE_FLAGS_CACHE_TTL`: seconds to cache feature flag results.
- `POSTHOG_FEATURE_FLAGS_CACHE_PREFIX`: cache key prefix for feature flag results.
- `POSTHOG_VALIDATE_ON_STARTUP`: validate configuration on app startup.
- `POSTHOG_VALIDATE_EVENT_NAME`: event used for validation.
- `POSTHOG_VALIDATE_DISTINCT_ID`: distinct ID used for validation.

## Notes

- Feature flag definition caching uses the configured Django cache backend and
  is enabled by default when a cache is available.
- Result caching for feature flags is opt-in by setting
  `POSTHOG_FEATURE_FLAGS_CACHE_TTL`. To preserve `$feature_flag_called` events,
  keep `send_feature_flag_events=True` (cache is skipped in that case).

## Example project

See `example/` for a minimal Django project that wires in the middleware and
shows event capture + feature flags.
