from django.http import HttpResponse, JsonResponse
from django import conf
from django.views.decorators.csrf import csrf_exempt
from proxy.views import proxy_view
import requests

def api_catalogue(request, *args, **kwargs):

    # file = open(str(conf.settings.BASE_DIR)+"/devdata/catalogue.json", "r")
    # data = file.read()
    # file.close()

    catalogue_url = conf.settings.CATALOGUE_URL+"/catalogue/api/records/?format=json&application__name=sss"
    print (catalogue_url)
    auth_request = requests.auth.HTTPBasicAuth(conf.settings.AUTH2_BASIC_AUTH_USER, conf.settings.AUTH2_BASIC_AUTH_PASSWORD)
    response = requests.get(catalogue_url, auth=auth_request)
    data  = response.text
    return HttpResponse(data, content_type='application/json')

def api_bfrs_region(request, *args, **kwargs):

    # file = open(str(conf.settings.BASE_DIR)+"/devdata/catalogue.json", "r")
    # data = file.read()
    # file.close()
    
    bfrs_region_url = conf.settings.BFRS_URL+"/api/v1/region/?format=json"
    auth_request = requests.auth.HTTPBasicAuth(conf.settings.AUTH2_BASIC_AUTH_USER, conf.settings.AUTH2_BASIC_AUTH_PASSWORD)
    response = requests.get(bfrs_region_url, auth=auth_request)
    data  = response.text
    return HttpResponse(data, content_type='application/json')

# @csrf_exempt
# def kmiProxyView(request, path):
    
#     from requests.auth import HTTPBasicAuth

#    
#     return proxy_view(request, remoteurl, basic_auth={"user": user, 'password' : password})    



# @csrf_exempt
# def kbProxyView(request, path):

    
#     return proxy_view(request, remoteurl, basic_auth={"user": user, 'password' : password})    