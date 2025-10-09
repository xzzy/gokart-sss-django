from django.core.management.base import BaseCommand
import requests
from django import conf
from django.core.cache import cache
import datetime
from sss import models
import traceback

class Command(BaseCommand):
    help = 'Fetch and cache catalogue data'
    command_name = 'fetch_and_cache_catalogue_data'

    def handle(self, *args, **kwargs):
        start_time = datetime.datetime.now()
        self.stdout.write(f"{start_time} : Starting Catalogue Cache Sync")

        try:
            log_entry, created = models.ManagementCommandStatus.objects.get_or_create(
                command=self.command_name
            )
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to access database for command status: {e}"))
            return

        try:
            catalogue_url = conf.settings.CATALOGUE_URL + "/catalogue/api/records/?format=json&application__name=sss"
            auth_request = requests.auth.HTTPBasicAuth(conf.settings.AUTH2_BASIC_AUTH_USER, conf.settings.AUTH2_BASIC_AUTH_PASSWORD)

            response = requests.get(catalogue_url, auth=auth_request)
            data = response.text
            
            if (response.status_code == 200):
                cache.delete('catalogue_cache_data')
                cache.set('catalogue_cache_data', data, 86400)
                
                end_time = datetime.datetime.now()
                duration_seconds = int((end_time - start_time).total_seconds())

                log_entry.completion_time = end_time
                log_entry.duration = duration_seconds
                log_entry.save()
                
                self.stdout.write(self.style.SUCCESS(f"Catalogue cache updated successfully in {duration_seconds} seconds."))

            else:
                # HTTP Request failed
                error_msg = f"Catalogue API returned status code {response.status_code}. Response: {data[:200]}"
                self.stderr.write(self.style.ERROR(error_msg))
                return

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"FATAL ERROR running {self.command_name}: {e}"))
            self.stderr.write(self.style.ERROR(traceback.format_exc()))
            return