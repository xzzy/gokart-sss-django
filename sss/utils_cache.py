from django.core.cache import cache
from sss.models import UserProfile, ProxyCache

def get_user_profile(user, session_key):
    cache_key = 'utils_cache.get_profile('+str(user.id)+':'+str(session_key)+')'
    profile_dumped_data = cache.get(cache_key)

    if profile_dumped_data is None:
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        cache.set(cache_key, user_profile, 86400)
    else:
       user_profile = profile_dumped_data
    return user_profile

def get_proxy_cache():
    proxy_cache_dumped_data =cache.get('utils_cache.get_proxy_cache()')
    proxy_cache_array = []

    if proxy_cache_dumped_data is None:
        proxy_cache_query = ProxyCache.objects.all()
        
        for pr in proxy_cache_query:
            proxy_cache_array.append({'layer_name': pr.layer_name, 'cache_expiry' : pr.cache_expiry})

        cache.set('utils_cache.get_proxy_cache()', proxy_cache_array, 86400)
    else:
       proxy_cache_array =  proxy_cache_dumped_data
    return proxy_cache_array