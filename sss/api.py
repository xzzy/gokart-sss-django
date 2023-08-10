from django.http import HttpResponse, JsonResponse
from django import conf
from django.views.decorators.csrf import csrf_exempt
from wagov_utils.components.proxy.views import proxy_view
from django.core.cache import cache
from django.template.loader import render_to_string
from sss import raster
import requests
import base64
import json
from io import BytesIO
from sss.models import UserProfile
from sss.serializers import ProfileSerializer, AccountDetailsSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

def api_catalogue(request, *args, **kwargs):

    # if DEV use this
    # file = open(str(conf.settings.BASE_DIR)+"/devdata/catalogue.json", "r")
    # data = file.read()
    # file.close()

    catalogue_url = conf.settings.CATALOGUE_URL+"/catalogue/api/records/?format=json&application__name=sss"    
    auth_request = requests.auth.HTTPBasicAuth(conf.settings.AUTH2_BASIC_AUTH_USER, conf.settings.AUTH2_BASIC_AUTH_PASSWORD)
    response = requests.get(catalogue_url, auth=auth_request)
    data  = response.text
    return HttpResponse(data, content_type='application/json')

def api_bfrs_region(request, *args, **kwargs):

    # if DEV use this
    # file = open(str(conf.settings.BASE_DIR)+"/devdata/catalogue.json", "r")
    # data = file.read()
    # file.close()
    
    bfrs_region_url = conf.settings.BFRS_URL+"/api/v1/region/?format=json"
    print (conf.settings.AUTH2_BASIC_AUTH_USER, conf.settings.AUTH2_BASIC_AUTH_PASSWORD)
    auth_request = requests.auth.HTTPBasicAuth(conf.settings.AUTH2_BASIC_AUTH_USER, conf.settings.AUTH2_BASIC_AUTH_PASSWORD)
    response = requests.get(bfrs_region_url, auth=auth_request)
    data  = response.text
    return HttpResponse(data, content_type='application/json')

@csrf_exempt
def kmiProxyView(request, path):
    # start move to django model
    cache_times_strings = [
        {'layer_name': 'mapbox-outdoors',
         'cache_expiry' : 172800
        },
        {'layer_name': 'fuel_age_nonforest_1_6yrs_cddp',
         'cache_expiry' : 300},  
        {'layer_name': 'state_map_base', 
         'cache_expiry' : 172800
        },
        {'layer_name': 'resource_tracking_live', 
         'cache_expiry' : 30
        } 
    ]
    # end move to django model
    CACHE_EXPIRY=300
    remoteurl = conf.settings.KMI_API_URL + '/' + path   
    query_string_remote_url=remoteurl+'?'+request.META['QUERY_STRING']
    proxy_response = None
    proxy_cache = cache.get(query_string_remote_url)
    #proxy_cache= None
    proxy_response_content = None
    base64_json = {}


    for cts in cache_times_strings:
        if cts['layer_name'] in query_string_remote_url:
            CACHE_EXPIRY = cts['cache_expiry']
        print (cts['layer_name'])

    print (CACHE_EXPIRY)
    if proxy_cache is None:
        proxy_response = proxy_view(request, remoteurl, basic_auth={"user": conf.settings.KMI_AUTH2_BASIC_AUTH_USER, 'password' : conf.settings.KMI_AUTH2_BASIC_AUTH_PASSWORD}, cookies={})    
        proxy_response_content_encoded = base64.b64encode(proxy_response.content)
        base64_json = {"status_code": proxy_response.status_code, "content_type": proxy_response.headers['content-type'], "content" : proxy_response_content_encoded.decode('utf-8'), "cache_expiry": CACHE_EXPIRY}
        if proxy_response.status_code == 200: 
            cache.set(query_string_remote_url, json.dumps(base64_json), CACHE_EXPIRY)
        else:
            cache.set(query_string_remote_url, json.dumps(base64_json), 15)
    else:
        print ("CACHED")
        print (query_string_remote_url)
        base64_json = json.loads(proxy_cache)
    proxy_response_content = base64.b64decode(base64_json["content"].encode())
    http_response =   HttpResponse(proxy_response_content, content_type=base64_json['content_type'], status=base64_json['status_code'])    
    http_response.headers['Django-Cache-Expiry']= str(base64_json['cache_expiry']) + " seconds"
    return http_response




@csrf_exempt
def kbProxyView(request, path):
    remoteurl = conf.settings.KB_API_URL + '/' + path
     
    proxy_response = None
    proxy_cache = cache.get(remoteurl+'?'+request.META['QUERY_STRING'])
    proxy_cache= None
    proxy_response_content = None
    base64_json = {}
    if proxy_cache is None:
        proxy_response = proxy_view(request, remoteurl, basic_auth={"user": conf.settings.KB_AUTH2_BASIC_AUTH_USER, 'password' : conf.settings.KB_AUTH2_BASIC_AUTH_PASSWORD}, cookies={})    
        proxy_response_content_encoded = base64.b64encode(proxy_response.content)
        base64_json = {"content_type": proxy_response.headers['content-type'], "content" : proxy_response_content_encoded.decode('utf-8')}

        cache.set(remoteurl+'?'+request.META['QUERY_STRING'], json.dumps(base64_json), 86400)
    else:
        # print ("CACHED")
        # print (remoteurl+'?'+request.META['QUERY_STRING'])
        base64_json = json.loads(proxy_cache)
    proxy_response_content = base64.b64decode(base64_json["content"].encode())
    return HttpResponse(proxy_response_content, content_type=base64_json['content_type'])    

def environment_config(request):
    context = {'settings': conf.settings}
    template_date = render_to_string('sss/environment_config.js', context)    
    return HttpResponse(template_date, content_type='text/javascript')


def sso_profile(request):
    data= '{"authenticated": true, "email": "test.test@dbca.wa.gov.au", "username": "test.test@dbca.wa.gov.au", "first_name": "Test", "last_name": "Test", "full_name": "Test Test", "groups": "TEST,TEST1,TEST_ADMIN_TEAM,TEST_DEV_TEAM", "logout_url": "/sso/auth_logout", "session_key": "000.000.000.000.000|AUTH2-01|000dddeeefffff|1-auth2018eeedddfffgghhhtttyuuhgg", "auth_cache_hit": "success", "Frame_Options": "DENY", "Content_Type_Options": "nosniff", "client_logon_ip": "000.000.000.000", "access_token": "eeddfffuuiiidlkdldkdkdldkllksdlkdlkkjasdlksajlkdjkhlsajkdsajdlkas", "access_token_created": "2023-07-19 10:24:54", "access_token_expireat": "2023-08-16 23:59:59", "idp": "staff"}'
    return HttpResponse(data, content_type='application/json')

def outlookmetadata(request):

    data = raster.outlookmetadata(request)
    #data = raster.test(request)
    return HttpResponse(json.dumps(data), content_type='application/json')

def api_profile(request, *args, **kwargs):
    user_logged_in = None
    if request.user.is_authenticated:
        user_logged_in = request.user
        try:
            user_profile = UserProfile.objects.get(user=user_logged_in)
            serializer = ProfileSerializer(user_profile)
            return HttpResponse(json.dumps(serializer.data), content_type='application/json')
        except serializers.ValidationError:
                raise serializers.ValidationError('Serializer not valid')
        except UserProfile.DoesNotExist:
            raise ValidationError('User profile for the logged in user does not exist')
    else:
        raise ValidationError('User is not authenticated')
    
def api_account(request, *args, **kwargs):
    user_logged_in = None
    if request.user.is_authenticated:
        user_logged_in = request.user
        try:
            user_profile = UserProfile.objects.get(user=user_logged_in)
            serializer = AccountDetailsSerializer(user_profile)
            return HttpResponse(json.dumps(serializer.data), content_type='application/json')
        except serializers.ValidationError:
                raise serializers.ValidationError('Serializer not valid')
        except UserProfile.DoesNotExist:
            raise ValidationError('User profile for the logged in user does not exist')
    else:
        raise ValidationError('User is not authenticated')


    