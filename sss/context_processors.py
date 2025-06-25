"""Context processors for the Django project."""


# Third-Party
from django import conf
from django import http
from sss.models import MapServer

# Typing
from typing import Any


def variables(request):

    kmi = MapServer.objects.filter(name='kmi').first()
    kmi_url = f"{request.scheme}://{request.get_host()}{kmi.url}" if kmi else None
    # Construct and return context  
    return {
#        "app_build_url": conf.settings.DEV_APP_BUILD_URL,
        "GIT_COMMIT_HASH": conf.settings.GIT_COMMIT_HASH,
        "DJANGO_SETTINGS": conf.settings,
        "settings": conf.settings,
        "kmi_url": kmi_url
    }