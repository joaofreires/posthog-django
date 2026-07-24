from __future__ import annotations

import posthog_django.client as client_module


def test_disabling_feature_flags_disables_local_evaluation(settings, monkeypatch):
    settings.POSTHOG_PROJECT_API_KEY = "phc_test"
    settings.POSTHOG_ENABLE_FEATURE_FLAGS = False

    client_options = {}

    class FakeClient:
        def __init__(self, project_api_key, **kwargs):
            client_options["project_api_key"] = project_api_key
            client_options.update(kwargs)

    monkeypatch.setattr(client_module, "Client", FakeClient)

    client_module._build_client()

    assert client_options["enable_local_evaluation"] is False
    assert client_options["flag_definition_cache_provider"] is None


def test_missing_personal_api_key_disables_local_evaluation(settings, monkeypatch):
    settings.POSTHOG_PROJECT_API_KEY = "phc_test"
    settings.POSTHOG_ENABLE_FEATURE_FLAGS = True
    settings.POSTHOG_ENABLE_LOCAL_EVALUATION = True
    settings.POSTHOG_PERSONAL_API_KEY = None

    client_options = {}

    class FakeClient:
        def __init__(self, project_api_key, **kwargs):
            client_options["project_api_key"] = project_api_key
            client_options.update(kwargs)

    monkeypatch.setattr(client_module, "Client", FakeClient)

    client_module._build_client()

    assert client_options["enable_local_evaluation"] is False
    assert client_options["flag_definition_cache_provider"] is None
