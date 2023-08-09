"""
URL configuration for sss project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# Third-Party
from django.contrib import admin
from django.urls import path, re_path

# Local
from sss import views
from sss import api

urlpatterns = [
    path('api/catalogue.json', api.api_catalogue, name='api_catalogue_api'),
    path('api/brfs-region.json', api.api_bfrs_region, name='api_bfrs_region_api'),
    path('admin/', admin.site.urls),
    path("", views.HomePage.as_view(), name="home"),
    path("outlookmetadata", api.outlookmetadata, name='api_outlookmetadata'),
    path("api/environment_config.js", api.environment_config, name='environment_config'),
    re_path('kmi-proxy/(?P<path>.*)', api.kmiProxyView),
    re_path('kb-proxy/(?P<path>.*)', api.kbProxyView),

    path("sso/profile", api.sso_profile)
]
