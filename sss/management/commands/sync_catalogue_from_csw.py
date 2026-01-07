from django.core.management.base import BaseCommand
import requests
from django import conf
from django.core.cache import cache
from sss import models
import os, errno
import time
from django.utils import timezone
import json
import hashlib
from django.utils import timezone
import logging

logger = logging.getLogger('cron_tasks')

class Command(BaseCommand):
    help = 'Sync GIS catalogue data from CSW'
    command_name = 'sync_catalogue_from_csw'

    def handle(self, *args, **kwargs):
        start_time = timezone.now()
        try:
            log_entry, created = models.ManagementCommandStatus.objects.get_or_create(
                command=self.command_name
            )
        except Exception as e:
            logger.error(f"Failed to access database for command status: {e}")
            return
        try:
            catalogue_url = conf.settings.CATALOGUE_URL + "/catalogue/api/records/?format=json&application__name=sss"
            auth_request = requests.auth.HTTPBasicAuth(conf.settings.AUTH2_BASIC_AUTH_USER, conf.settings.AUTH2_BASIC_AUTH_PASSWORD)
            response = requests.get(catalogue_url, auth=auth_request)
            catalogue_data = response.json()
            catalogue_ids = []
            for cd in catalogue_data:
                logger.info(cd['id'])
                logger.info(cd['identifier'])
                catalogue_ids.append(cd['id'])
                csw_catalogue = models.CatalogueSyncCSW.objects.filter(csw_id=cd['id'])

                if csw_catalogue.count() > 0: 
                    csw_obj = models.CatalogueSyncCSW.objects.get(csw_id=cd['id'])
                    csw_json_hash = hashlib.md5(json.dumps(cd).encode('utf-8'))
                    sss_json_hash = hashlib.md5(csw_obj.json_data.encode('utf-8'))

                    if csw_obj.identifier != cd['identifier'] or csw_json_hash.hexdigest() != sss_json_hash.hexdigest():                        
                        csw_obj.identifier=cd['identifier']
                        csw_obj.json_data=json.dumps(cd)
                        # csw_obj.active=True
                        csw_obj.updated = timezone.now() 
                        csw_obj.removed_from_csw=False
                        csw_obj.save()
                        logger.info("Updated: {} - {}".format(cd['id'], cd['identifier']))
                        pass
                else:
                    models.CatalogueSyncCSW.objects.create(csw_id=cd['id'],
                                                           identifier=cd['identifier'],
                                                           json_data=json.dumps(cd),
                                                           active=True,
                                                           removed_from_csw=False
                                                           )
                    logger.info("Creating: {} - {}".format(cd['id'], cd['identifier']))

            for cs_csw in models.CatalogueSyncCSW.objects.all():

                if cs_csw.csw_id in catalogue_ids:
                    if cs_csw.removed_from_csw is True:
                        cs_csw.updated = timezone.now() 
                        cs_csw.removed_from_csw=False 
                        cs_csw.save()                   
                else:
                    if cs_csw.removed_from_csw is False:
                        cs_csw.updated = timezone.now() 
                        cs_csw.removed_from_csw=True
                        cs_csw.save()
                

            # This block only runs on successful completion
            end_time = timezone.now()
            duration_seconds = int((end_time - start_time).total_seconds())

            log_entry.completion_time = end_time
            log_entry.duration = duration_seconds
            log_entry.save()
            
            logger.info(f"CSW catalogue synced successfully in {duration_seconds} seconds.")

#            print (data)

        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
