from django.core.management.base import BaseCommand
import requests
from django import conf
from django.core.cache import cache

class Command(BaseCommand):
    help = 'Fetch and cache bfrs region data'

    def handle(self, *args, **kwargs):
        try:
            bfrs_region_url = conf.settings.BFRS_URL+"/api/v1/region/?format=json"
            auth_request = requests.auth.HTTPBasicAuth(conf.settings.AUTH2_BASIC_AUTH_USER, conf.settings.AUTH2_BASIC_AUTH_PASSWORD)
            response = requests.get(bfrs_region_url, auth=auth_request)
            data  = response.text
            if (response.status_code == 200):
                cache.delete('bfrs_region_cache_data')
                cache.set('bfrs_region_cache_data', data, 86400)

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred: {str(e)}"))
