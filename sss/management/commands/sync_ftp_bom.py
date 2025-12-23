from django.core.management.base import BaseCommand
import requests
from osgeo import gdal
import subprocess
from django import conf
import ftplib
import os
import time
import datetime
from django.utils import timezone
import shutil
import traceback
from sss import models
import logging

logger = logging.getLogger('cron_tasks')


class Command(BaseCommand):
    help = 'Sync BOM Data files to local storage'
    command_name = 'sync_ftp_bom'

    def handle(self, *args, **kwargs):
        start_time = timezone.now()
        logger.info(f"Starting BOM Sync")

        # Get or create the single log entry for this command
        try:
            log_entry, created = models.ManagementCommandStatus.objects.get_or_create(
                command=self.command_name
            )
        except Exception as e:
            logger.error(f"Failed to access database for command status: {e}")
            return

        try:
            BOM_HOME_LOCAL = conf.settings.BOM_HOME
            BOM_SYNC_FOLDER = conf.settings.BOM_SYNC_FOLDER
            bom_ftp_server = conf.settings.BOM_FTP_SERVER
            bom_ftp_username = conf.settings.BOM_FTP_USERNAME
            bom_ftp_password = conf.settings.BOM_FTP_PASSWORD
            bom_ftp_directory = conf.settings.BOM_FTP_DIRECTORY

            temp_dir = os.path.join(BOM_SYNC_FOLDER)
            os.makedirs(temp_dir, exist_ok=True)
            os.makedirs(os.path.join(BOM_HOME_LOCAL, bom_ftp_directory), exist_ok=True)

            try:
                ftp_session = ftplib.FTP(bom_ftp_server, bom_ftp_username, bom_ftp_password)
                ftp_session.cwd(bom_ftp_directory)
            except Exception:
                logger.error("Could not connect to FTP server.")
                return

            bsl = models.BomSyncList.objects.filter(active=True)

            # Clear out temp directory
            files = os.listdir(temp_dir)
            for f in files:
                file_path = os.path.join(temp_dir, f)
                if os.path.isfile(file_path):
                    os.remove(file_path)

            for file in bsl:
                local_file = os.path.join(BOM_HOME_LOCAL, bom_ftp_directory, file.file_name)
                temp_local_file = os.path.join(temp_dir, file.file_name)
                
                try:
                    file_list_count = ftp_session.nlst(file.file_name)
                except ftplib.all_errors as e:
                    logger.error(f"FTP listing failed for {file.file_name}. Reason: {e}")
                    continue
                
                if len(file_list_count) > 0:
                    try:
                        remote_datetime = ftp_session.voidcmd("MDTM " + file.file_name)[4:].strip()
                        remote_timestamp = time.mktime(time.strptime(remote_datetime, '%Y%m%d%H%M%S'))
                        remote_file_size = ftp_session.size(file.file_name)
                    except ftplib.all_errors as e:
                        logger.error(f"FTP file details failed for {file.file_name}. Reason: {e}")
                        continue

                    local_timestamp = None
                    local_file_size = 0
                    if os.path.exists(local_file):
                        local_timestamp = os.path.getmtime(local_file)
                        local_file_size = os.path.getsize(local_file)
                        
                    if local_timestamp == remote_timestamp and local_file_size == remote_file_size:
                        logger.info(f"No changes to file : {file.file_name}")
                    else:
                        logger.info(f"Retrieving File : {file.file_name}")
                        try:
                            with open(temp_local_file, 'wb') as temp_file:
                                ftp_session.retrbinary("RETR " + file.file_name, temp_file.write)
                            os.utime(temp_local_file, (remote_timestamp, remote_timestamp))
                        except Exception:
                            logger.error(f"Unable to retrieve file : {file.file_name}")
                            logger.error(traceback.format_exc())
                            continue
                else:
                    logger.error(f"file does not exist on remote server : {file.file_name}")
                    continue

            ftp_session.close()

            for temp_file_name in os.listdir(temp_dir):
                temp_file_path = os.path.join(temp_dir, temp_file_name)
                local_file_path = os.path.join(BOM_HOME_LOCAL, bom_ftp_directory, temp_file_name)
                if temp_file_name.endswith('.nc.gz'):
                    try:
                        subprocess.check_call(["gzip", "-k", "-f", "-q", "-d", temp_file_path])
                        unzipped_file_path = temp_file_path[:-3]

                        # try:
                        #     #Checking if the unzipped file can be opened by GDAL
                        #     gdal.Open(unzipped_file_path)
                        # except Exception:
                        #     try:
                        #         if os.path.exists(unzipped_file_path):
                        #             os.remove(unzipped_file_path)
                        #             logger.error("file could not be opened, REMOVING FILE: %s", unzipped_file_path)
                        #         if os.path.exists(temp_file_path):
                        #             logger.error("file could not be opened, REMOVING FILE: %s", temp_file_path)
                        #             os.remove(temp_file_path)
                        #     except Exception:
                        #         pass
                        #     continue
                        
                        # Atomic update for .nc.gz file
                        tmp_local_file_path = local_file_path + ".tmp"
                        shutil.copy2(temp_file_path, tmp_local_file_path)
                        os.rename(tmp_local_file_path, local_file_path)

                        # Atomic update for .nc file
                        dest_path = os.path.join(BOM_HOME_LOCAL, bom_ftp_directory, os.path.basename(unzipped_file_path))
                        tmp_dest_path = dest_path + ".tmp"
                        shutil.copy2(unzipped_file_path, tmp_dest_path)
                        os.rename(tmp_dest_path, dest_path)

                        os.remove(temp_file_path)
                        os.remove(unzipped_file_path)
                        
                    except subprocess.CalledProcessError:
                        logger.error(f"Unzipping failed for {temp_file_name}")
                        return
                
                elif temp_file_name.endswith('.nc'):
                    try:
                        # try:
                        #     #Checking if the file can be opened by GDAL
                        #     gdal.Open(temp_file_path)
                        # except Exception:
                        #     try:
                        #         if os.path.exists(temp_file_path):
                        #             logger.error("file could not be opened, REMOVING FILE: %s", temp_file_path)
                        #             os.remove(temp_file_path)
                        #     except Exception:
                        #         pass
                        #     continue

                        # Atomic update for .nc file
                        tmp_local_file_path = local_file_path + ".tmp"
                        shutil.copy2(temp_file_path, tmp_local_file_path)
                        os.rename(tmp_local_file_path, local_file_path)

                        os.remove(temp_file_path)
                    except Exception:
                        logger.error(f"File copy/delete failed for {temp_file_name}")
                        return
            
            # This block only runs on successful completion
            end_time = timezone.now()
            duration_seconds = int((end_time - start_time).total_seconds())

            log_entry.completion_time = end_time
            log_entry.duration = duration_seconds
            log_entry.save()
            
            logger.info(f"BOM Sync completed successfully in {duration_seconds} seconds.")

        except Exception as e:
            # Any unhandled exceptions will be caught here, but no database update will be made
            logger.error("ERROR running BOM SYNC")
            logger.error(f"An error occurred: {str(e)}")
            return