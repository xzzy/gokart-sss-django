from django.core.management.base import BaseCommand
import requests
from django import conf
from django.core.cache import cache
import ftplib
import os, errno
import time
import datetime
from sss import models


class Command(BaseCommand):
    help = 'Sync BOM Data files to local storage'

    def handle(self, *args, **kwargs):
        try:
            current_time = datetime.datetime.now()
            print (str(current_time)+ " : Starting BOM Sync")
            BOM_HOME_LOCAL = conf.settings.BOM_HOME
            bom_ftp_server = conf.settings.BOM_FTP_SERVER
            bom_ftp_username = conf.settings.BOM_FTP_USERNAME
            bom_ftp_password = conf.settings.BOM_FTP_PASSWORD
            bom_ftp_directory = conf.settings.BOM_FTP_DIRECTORY

            try:
                os.makedirs(BOM_HOME_LOCAL + '/' + bom_ftp_directory)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
            
            ftp_session = ftplib.FTP(bom_ftp_server,bom_ftp_username,bom_ftp_password)
            ftp_session.cwd(bom_ftp_directory)
           
            
            files = ftp_session.nlst()
            #print (files)

            bsl = models.BomSyncList.objects.filter(active=True)
            for file in bsl:
                current_time = datetime.datetime.now()
                local_file = BOM_HOME_LOCAL + '/' + bom_ftp_directory + '/' + file.file_name                            
                file_list_count = ftp_session.nlst(file.file_name)
                if len(file_list_count) > 0:
                    remote_datetime = ftp_session.voidcmd("MDTM " + file.file_name)[4:].strip() 
                    remote_timestamp = time.mktime(time.strptime(remote_datetime, '%Y%m%d%H%M%S'))
                    remote_file_size = ftp_session.size(file.file_name)

                    local_timestamp = None
                    local_file_size = 0 
                    if os.path.exists(local_file): 
                        local_timestamp = os.path.getmtime(local_file)
                        local_file_size = os.path.getsize(local_file)

                    
                    if local_timestamp == remote_timestamp and local_file_size == remote_file_size:
                        print (str(current_time)+ " : No changes to file : "+ file.file_name)
                    else:
                        print (str(current_time)+ " : Retreiving File : "+ file.file_name)
                        try: 
                            ftp_session.retrbinary("RETR " + file.file_name ,open(local_file, 'wb').write)
                            os.utime(local_file, (remote_timestamp, remote_timestamp))
                        except Exception as e:
                            print (str(current_time)+ " : ERROR: Unable to retreive file : "+ file.file_name )
                            print (str(current_time)+ ":" + str(e))
                else:
                    print (str(current_time)+ " : ERROR: file does not exist on remote server : "+ file.file_name )

            
        except Exception as e:
            print ("ERROR running BOM SYNC")
            print (e)
            self.stderr.write(self.style.ERROR(f"An error occurred: {str(e)}"))
