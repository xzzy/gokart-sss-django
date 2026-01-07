from django.core.management.base import BaseCommand
import requests
from django import conf
from django.core.cache import cache
from django.utils import timezone
from sss import models
import traceback
import logging

logger = logging.getLogger('cron_tasks')

class Command(BaseCommand):
    help = 'Fetch and cache bfrs region data'
    command_name = 'fetch_and_cache_bfrs_region_data'

    def handle(self, *args, **kwargs):
        start_time = timezone.now()
        logger.info("Starting BFRS Region Cache Sync")

        try:
            log_entry, created = models.ManagementCommandStatus.objects.get_or_create(
                command=self.command_name
            )
        except Exception as e:
            logger.error(f"Failed to access database for command status: {e}")
            return

        try:
            bfrs_region_url = conf.settings.BFRS_URL + "/api/v1/region/?format=json"
            auth_request = requests.auth.HTTPBasicAuth(conf.settings.AUTH2_BASIC_AUTH_USER, conf.settings.AUTH2_BASIC_AUTH_PASSWORD)

            response = requests.get(bfrs_region_url, auth=auth_request)
            data = response.text
            
            if (response.status_code == 200):
                cache.delete('bfrs_region_cache_data')
                cache.set('bfrs_region_cache_data', data, 86400)

                end_time = timezone.now()
                duration_seconds = int((end_time - start_time).total_seconds())

                log_entry.completion_time = end_time
                log_entry.duration = duration_seconds
                log_entry.save()
                
                logger.info(f"BFRS Region cache updated successfully in {duration_seconds} seconds.")

            else:
                error_msg = f"BFRS Region API returned status code {response.status_code}. Response: {data[:200]}"
                logger.error(error_msg)
                return

        except Exception as e:
            logger.error(f"FATAL ERROR running {self.command_name}: {e}")
            logger.error(traceback.format_exc())
            return