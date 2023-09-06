# my_catalogue_task.py

from django.core.management.base import BaseCommand
import requests
from django import conf
from django.core.cache import cache

class Command(BaseCommand):
    help = 'Fetch and cache catalogue data'

    def handle(self, *args, **kwargs):
        try:
            catalogue_url = conf.settings.CATALOGUE_URL + "/catalogue/api/records/?format=json&application__name=sss"
            auth_request = requests.auth.HTTPBasicAuth(conf.settings.AUTH2_BASIC_AUTH_USER, conf.settings.AUTH2_BASIC_AUTH_PASSWORD)
            response = requests.get(catalogue_url, auth=auth_request)
            data = response.text
            if (response.status_code == 200):
                cache.delete('catalogue_cache_data')
                cache.set('catalogue_cache_data', data, 86400)

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred: {str(e)}"))
