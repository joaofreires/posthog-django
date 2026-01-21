from django.http import JsonResponse

from posthog_django import capture
from posthog_django import capture_exception
from posthog_django import feature_enabled
from posthog_django import get_feature_flag


def index(request):
    capture("page_view", request=request, properties={"path": request.path})
    return JsonResponse({"status": "ok"})


def flags(request):
    enabled = feature_enabled("new-homepage", request=request)
    variant = get_feature_flag("pricing-test", request=request)
    return JsonResponse({"new_homepage": enabled, "pricing_variant": variant})


def error(request):
    try:
        raise RuntimeError("Example PostHog error page")
    except Exception as exc:
        capture_exception(exc, request=request)
        return JsonResponse({"error": "example exception captured"}, status=500)


def middleware_captured_error(request):
    dividend = 10
    divisor = 0
    quotient = dividend / divisor  # This will raise a ZeroDivisionError
    return JsonResponse({"quotient": quotient})
