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
    path('api/profile.json', api.api_profile, name='api_profile_api'),
    path('api/account.json', api.api_account, name='api_account_api'),
    path('api/spatial', api.spatial, name='api_spatial_api'),
    path('api/mapbox.json', api.api_mapbox, name='api_mapbox_api'),
    path('admin/', admin.site.urls),
    path("", views.HomePage.as_view(), name="home"),
    path("outlookmetadata", api.outlookmetadata, name='api_outlookmetadata'),
    path("api/environment_config.js", api.environment_config, name='environment_config'),
    path("api/cataloguev2.json", api.cataloguev2, name='catalogue_example'),
    re_path(
        "geoproxy/(?P<request_path>[A-Za-z0-9-]+)/(?P<path>.*)",
        api.mapProxyView,
    ),
    re_path('weatheroutlook/(?P<fmt>.*)', api.weatheroutlook),
    re_path('gdal/(?P<fmt>.*)', api.gdal),
    re_path('ogrinfo', api.gdal_ogrinfo),
    re_path('download/(?P<fmt>.*)', api.gdal_download),
    path("sso/profile", api.sso_profile),
    re_path('hi8/(?P<target>.*)',api.himawari8),
]
