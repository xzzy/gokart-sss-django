from django.core.management.base import BaseCommand
import requests
from django import conf
from django.core.cache import cache
from sss import models
import os, errno
import time
import datetime
import json
import hashlib
from django.utils import timezone



class Command(BaseCommand):
    help = 'Sync GIS catalogue data from CSW'

    def handle(self, *args, **kwargs):
        try:
            catalogue_url = conf.settings.CATALOGUE_URL + "/catalogue/api/records/?format=json&application__name=sss"
            auth_request = requests.auth.HTTPBasicAuth(conf.settings.AUTH2_BASIC_AUTH_USER, conf.settings.AUTH2_BASIC_AUTH_PASSWORD)
            response = requests.get(catalogue_url, auth=auth_request)
            catalogue_data = response.json()
            catalogue_ids = []
            for cd in catalogue_data:
                print (cd['id'])
                print (cd['identifier'])
                catalogue_ids.append(cd['id'])
                csw_catalogue = models.CatalogueSyncCSW.objects.filter(csw_id=cd['id'])

                if csw_catalogue.count() > 0: 
                    csw_obj = models.CatalogueSyncCSW.objects.get(csw_id=cd['id'])
                    csw_json_hash = hashlib.md5(json.dumps(cd).encode('utf-8'))
                    sss_json_hash = hashlib.md5(csw_obj.json_data.encode('utf-8'))

                    if csw_obj.identifier != cd['identifier'] or csw_json_hash.hexdigest() != sss_json_hash.hexdigest():                        
                        csw_obj.identifier=cd['identifier']
                        csw_obj.json_data=json.dumps(cd)
                        csw_obj.active=True
                        csw_obj.updated = timezone.now() 
                        csw_obj.removed_from_csw=False
                        csw_obj.save()
                        print ("Updated: {} - {}".format(cd['id'], cd['identifier']))
                        pass
                else:
                    models.CatalogueSyncCSW.objects.create(csw_id=cd['id'],
                                                           identifier=cd['identifier'],
                                                           json_data=json.dumps(cd),
                                                           active=True,
                                                           removed_from_csw=False
                                                           )
                    print ("Creating: {} - {}".format(cd['id'], cd['identifier']))

            for cs_csw in models.CatalogueSyncCSW.objects.all():

                if cs_csw.csw_id in catalogue_ids:
                    if cs_csw.removed_from_csw is True:
                        csw_obj.updated = timezone.now() 
                        cs_csw.removed_from_csw=False  
                        csw_obj.save()                      
                else:
                    if cs_csw.removed_from_csw is False:
                        csw_obj.updated = timezone.now() 
                        cs_csw.removed_from_csw=True
                        csw_obj.save()



#            print (data)

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred: {str(e)}"))
            print (e)
