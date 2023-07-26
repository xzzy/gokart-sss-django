"""Context processors for the Django project."""


# Third-Party
from django import conf
from django import http

# Typing
from typing import Any


def variables(request):

    # Construct and return context  
    return {
#        "app_build_url": conf.settings.DEV_APP_BUILD_URL,
        "GIT_COMMIT_HASH": conf.settings.GIT_COMMIT_HASH,
        "DJANGO_SETTINGS": conf.settings,
        "settings": conf.settings

    }