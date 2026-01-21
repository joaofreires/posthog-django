# Example Django Project

This is a minimal Django project that demonstrates using `posthog_django`.

## Quick start

```bash
cd example
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Configure PostHog

Edit `example_project/settings.py` and set:

```python
POSTHOG_PROJECT_API_KEY = "phc_your_project_key"
POSTHOG_PERSONAL_API_KEY = "phx_your_personal_key"
POSTHOG_HOST = "https://app.posthog.com"
POSTHOG_ERROR_MODE = "log"  # log | raise | ignore
POSTHOG_VALIDATE_ON_STARTUP = True
```

Then visit:
- `http://127.0.0.1:8000/` to capture a `page_view` event
- `http://127.0.0.1:8000/flags/` to evaluate feature flags
- `http://127.0.0.1:8000/error/` to send a captured exception

You can also set environment variables and read them in settings if you prefer.
