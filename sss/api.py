from django.http import HttpResponse, JsonResponse
from django import conf
from django.views.decorators.csrf import csrf_exempt
from wagov_utils.components.proxy.views import proxy_view
from django.core.cache import cache
from django.template.loader import render_to_string
from sss import raster
import requests
import base64
import datetime
import json
from io import BytesIO
from sss.models import UserProfile
from sss.serializers import ProfileSerializer, AccountDetailsSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from sss import utils_cache

def api_catalogue(request, *args, **kwargs):
    if request.user.is_authenticated:

        # if DEV use this
        # file = open(str(conf.settings.BASE_DIR)+"/devdata/catalogue.json", "r")
        # data = file.read()
        # file.close()

        catalogue_url = conf.settings.CATALOGUE_URL+"/catalogue/api/records/?format=json&application__name=sss"    
        auth_request = requests.auth.HTTPBasicAuth(conf.settings.AUTH2_BASIC_AUTH_USER, conf.settings.AUTH2_BASIC_AUTH_PASSWORD)
        response = requests.get(catalogue_url, auth=auth_request)
        data  = response.text
        return HttpResponse(data, content_type='application/json')
    else:
        raise ValidationError('User is not authenticated')
    
def api_bfrs_region(request, *args, **kwargs):
    if request.user.is_authenticated:

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
    else:
        raise ValidationError('User is not authenticated')
    

# @csrf_exempt
# def kmiProxyView(request, path):
#     # start move to django model
#     # cache_times_strings = [
#     #     {'layer_name': 'mapbox-outdoors',
#     #      'cache_expiry' : 172800
#     #     },
#     #     {'layer_name': 'fuel_age_nonforest_1_6yrs_cddp',
#     #      'cache_expiry' : 300},  
#     #     {'layer_name': 'state_map_base', 
#     #      'cache_expiry' : 172800
#     #     },
#     #     {'layer_name': 'resource_tracking_live', 
#     #      'cache_expiry' : 30
#     #     } 
#     # ]
#     cache_times_strings = utils_cache.get_proxy_cache()
#     # end move to django model
#     CACHE_EXPIRY=300
#     remoteurl = conf.settings.KMI_API_URL + '/' + path   
#     query_string_remote_url=remoteurl+'?'+request.META['QUERY_STRING']
#     proxy_response = None
#     proxy_cache = cache.get(query_string_remote_url)
#     #proxy_cache= None
#     proxy_response_content = None
#     base64_json = {}


#     for cts in cache_times_strings:
#         if cts['layer_name'] in query_string_remote_url:
#             CACHE_EXPIRY = cts['cache_expiry']
#         print (cts['layer_name'])

#     print (CACHE_EXPIRY)
#     if proxy_cache is None:
#         proxy_response = proxy_view(request, remoteurl, basic_auth={"user": conf.settings.KMI_AUTH2_BASIC_AUTH_USER, 'password' : conf.settings.KMI_AUTH2_BASIC_AUTH_PASSWORD}, cookies={})    
#         proxy_response_content_encoded = base64.b64encode(proxy_response.content)
#         base64_json = {"status_code": proxy_response.status_code, "content_type": proxy_response.headers['content-type'], "content" : proxy_response_content_encoded.decode('utf-8'), "cache_expiry": CACHE_EXPIRY}
#         if proxy_response.status_code == 200: 
#             cache.set(query_string_remote_url, json.dumps(base64_json), CACHE_EXPIRY)
#         else:
#             cache.set(query_string_remote_url, json.dumps(base64_json), 15)
#     else:
#         print ("CACHED")
#         print (query_string_remote_url)
#         base64_json = json.loads(proxy_cache)
#     proxy_response_content = base64.b64decode(base64_json["content"].encode())
#     http_response =   HttpResponse(proxy_response_content, content_type=base64_json['content_type'], status=base64_json['status_code'])    
#     http_response.headers['Django-Cache-Expiry']= str(base64_json['cache_expiry']) + " seconds"
#     return http_response

def process_proxy(request, remoteurl, queryString, auth_user, auth_password):
    proxy_cache= None
    proxy_response = None
    proxy_response_content = None
    base64_json = {}
    query_string_remote_url=remoteurl+'?'+queryString

    cache_times_strings = utils_cache.get_proxy_cache()
    CACHE_EXPIRY=300

    proxy_cache = cache.get(query_string_remote_url)

    for cts in cache_times_strings:
        if cts['layer_name'] in query_string_remote_url:
            CACHE_EXPIRY = cts['cache_expiry']
        print (cts['layer_name'])

    print (CACHE_EXPIRY)
    proxy_cache = None
    if proxy_cache is None:
        auth_details = None
        if auth_user is None and auth_password is None:
            auth_details = None
        else:
            auth_details = {"user": auth_user, 'password' : auth_password}
        proxy_response = proxy_view(request, remoteurl, basic_auth=auth_details, cookies={})    
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
def mapProxyView(request, path):
    if request.user.is_authenticated:
        queryString = request.META['QUERY_STRING']
        remoteurl = None
        auth_user = None
        auth_password = None

        if 'kmi-proxy' in request.path:
            remoteurl = conf.settings.KMI_API_URL + '/' + path 
            auth_user = conf.settings.KMI_AUTH2_BASIC_AUTH_USER
            auth_password = conf.settings.KMI_AUTH2_BASIC_AUTH_PASSWORD
        
        elif 'kb-proxy' in request.path:
            remoteurl = conf.settings.KMI_API_URL + '/' + path 
            auth_user = conf.settings.KB_AUTH2_BASIC_AUTH_USER
            auth_password = conf.settings.KB_AUTH2_BASIC_AUTH_PASSWORD
        
        elif 'hotspots-proxy' in request.path:
            remoteurl = conf.settings.HOTSPOT_URL + '/' + path

        response = process_proxy(request, remoteurl, queryString, auth_user, auth_password)
        return response
    else:
        raise ValidationError('User is not authenticated')
    
   

# @csrf_exempt
# def kbProxyView(request, path):
#     remoteurl = conf.settings.KB_API_URL + '/' + path
     
#     proxy_response = None
#     proxy_cache = cache.get(remoteurl+'?'+request.META['QUERY_STRING'])
#     proxy_cache= None
#     proxy_response_content = None
#     base64_json = {}
#     if proxy_cache is None:
#         proxy_response = proxy_view(request, remoteurl, basic_auth={"user": conf.settings.KB_AUTH2_BASIC_AUTH_USER, 'password' : conf.settings.KB_AUTH2_BASIC_AUTH_PASSWORD}, cookies={})    
#         proxy_response_content_encoded = base64.b64encode(proxy_response.content)
#         base64_json = {"content_type": proxy_response.headers['content-type'], "content" : proxy_response_content_encoded.decode('utf-8')}

#         cache.set(remoteurl+'?'+request.META['QUERY_STRING'], json.dumps(base64_json), 86400)
#     else:
#         # print ("CACHED")
#         # print (remoteurl+'?'+request.META['QUERY_STRING'])
#         base64_json = json.loads(proxy_cache)
#     proxy_response_content = base64.b64decode(base64_json["content"].encode())
#     return HttpResponse(proxy_response_content, content_type=base64_json['content_type'])    

def environment_config(request):
    context = {'settings': conf.settings}
    template_date = render_to_string('sss/environment_config.js', context)    
    return HttpResponse(template_date, content_type='text/javascript')


def sso_profile(request):
    data= '{"authenticated": true, "email": "test.test@dbca.wa.gov.au", "username": "test.test@dbca.wa.gov.au", "first_name": "Test", "last_name": "Test", "full_name": "Test Test", "groups": "TEST,TEST1,TEST_ADMIN_TEAM,TEST_DEV_TEAM", "logout_url": "/sso/auth_logout", "session_key": "000.000.000.000.000|AUTH2-01|000dddeeefffff|1-auth2018eeedddfffgghhhtttyuuhgg", "auth_cache_hit": "success", "Frame_Options": "DENY", "Content_Type_Options": "nosniff", "client_logon_ip": "000.000.000.000", "access_token": "eeddfffuuiiidlkdldkdkdldkllksdlkdlkkjasdlksajlkdjkhlsajkdsajdlkas", "access_token_created": "2023-07-19 10:24:54", "access_token_expireat": "2023-08-16 23:59:59", "idp": "staff"}'
    return HttpResponse(data, content_type='application/json')

def outlookmetadata(request):

    data = raster.outlookmetadata(request)
    #print ("WEather")
    #print (data)    
    #data = raster.test(request)
    return HttpResponse(json.dumps(data, default=str), content_type='application/json')

@csrf_exempt
def weatheroutlook(request, fmt):
    if request.user.is_authenticated:

        data = raster.weatheroutlook(request, fmt)

        if fmt == 'json':
            content_type = 'application/json'
        elif fmt == 'amicus':
            content_type = 'application/xml'
        elif fmt == 'html':
            content_type = 'text/html'
        else: 
            content_type = 'text/html'
        
        response = HttpResponse(data, content_type=content_type)    
        if fmt == 'json':
            response["Content-Disposition"] = "attachment;filename='weather_outlook_{}.json'".format(datetime.datetime.strftime(datetime.datetime.now(),"%Y%m%d_%H%M%S"))
        return response
    else:
        raise ValidationError('User is not authenticated')

def api_profile(request, *args, **kwargs):
    user_logged_in = None
    if request.user.is_authenticated:
        user_logged_in = request.user
        try:
            user_profile = utils_cache.get_user_profile(user_logged_in, request.session.session_key)
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
            user_profile = utils_cache.get_user_profile(user_logged_in, request.session.session_key)
            serializer = AccountDetailsSerializer(user_profile)
            return HttpResponse(json.dumps(serializer.data), content_type='application/json')
        except serializers.ValidationError:
                raise serializers.ValidationError('Serializer not valid')
        except UserProfile.DoesNotExist:
            raise ValidationError('User profile for the logged in user does not exist')
    else:
        raise ValidationError('User is not authenticated')
    
def api_mapbox(request, *args, **kwargs):
    if request.user.is_authenticated:

        geo_str = request.GET.get('geo_str')
        country = request.GET.get('country')
        proximity = request.GET.get('proximity')
        access_token = conf.settings.MAPBOX_ACCESS_TOKEN
        mapbox_url = conf.settings.MAPBOX_URL

        params = {
            'country': country,
            'proximity':proximity,
            'access_token': access_token 
        }
        headers = {
            # 'proxy_ssl_server_name': 'on',
            # 'resolver': '127.0.0.0',
            'proxy_set_header': 'Host api.mapbox.com',
            'proxy_hide_header': 'Access-Control-Allow-Credentials',
            'proxy_hide_header': 'Access-Control-Allow-Headers',
            'proxy_hide_header': 'Access-Control-Allow-Methods',
            'proxy_hide_header': 'Access-Control-Allow-Origin',
            'proxy_hide_header': 'Access-Control-Expose-Headers',
            'proxy_hide_header': 'Vary',
            'include': 'custom/cors',
            'proxy_pass': 'https://api.mapbox.com'
        }


        response = requests.get(mapbox_url + '/geocoding/v5/mapbox.places/' + geo_str + '.json', params=params, headers=headers)

        return HttpResponse(response, content_type='application/json')
    else:
        raise ValidationError('User is not authenticated')


    