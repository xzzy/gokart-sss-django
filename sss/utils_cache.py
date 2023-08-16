from django.core.cache import cache
from sss.models import UserProfile

def get_user_profile(user, session_key):
    cache_key = 'utils_cache.get_profile('+str(user.id)+':'+str(session_key)+')'
    profile_dumped_data = cache.get(cache_key)

    if profile_dumped_data is None:
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        cache.set(cache_key, user_profile, 86400)
    else:
       user_profile = profile_dumped_data
    return user_profile