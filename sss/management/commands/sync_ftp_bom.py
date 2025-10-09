from django.core.management.base import BaseCommand
import requests
import subprocess
from django import conf
import ftplib
import os
import time
import datetime
import shutil
import traceback
from sss import models

class Command(BaseCommand):
    help = 'Sync BOM Data files to local storage'
    command_name = 'sync_ftp_bom'

    def handle(self, *args, **kwargs):
        start_time = datetime.datetime.now()
        self.stdout.write(f"{start_time} : Starting BOM Sync")

        # Get or create the single log entry for this command
        try:
            log_entry, created = models.ManagementCommandStatus.objects.get_or_create(
                command=self.command_name
            )
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to access database for command status: {e}"))
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
                self.stderr.write(self.style.ERROR("ERROR: Could not connect to FTP server."))
                return

            bsl = models.BomSyncList.objects.filter(active=True)
            for file in bsl:
                current_time = datetime.datetime.now()
                local_file = os.path.join(BOM_HOME_LOCAL, bom_ftp_directory, file.file_name)
                temp_local_file = os.path.join(temp_dir, file.file_name)
                
                try:
                    file_list_count = ftp_session.nlst(file.file_name)
                except ftplib.all_errors as e:
                    self.stderr.write(self.style.ERROR(f"ERROR: FTP listing failed for {file.file_name}. Reason: {e}"))
                    return
                
                if len(file_list_count) > 0:
                    try:
                        remote_datetime = ftp_session.voidcmd("MDTM " + file.file_name)[4:].strip()
                        remote_timestamp = time.mktime(time.strptime(remote_datetime, '%Y%m%d%H%M%S'))
                        remote_file_size = ftp_session.size(file.file_name)
                    except ftplib.all_errors as e:
                        self.stderr.write(self.style.ERROR(f"ERROR: FTP file details failed for {file.file_name}. Reason: {e}"))
                        return

                    local_timestamp = None
                    local_file_size = 0
                    if os.path.exists(local_file):
                        local_timestamp = os.path.getmtime(local_file)
                        local_file_size = os.path.getsize(local_file)
                        
                    if local_timestamp == remote_timestamp and local_file_size == remote_file_size:
                        self.stdout.write(f"{current_time} : No changes to file : {file.file_name}")
                    else:
                        self.stdout.write(f"{current_time} : Retrieving File : {file.file_name}")
                        try:
                            with open(temp_local_file, 'wb') as temp_file:
                                ftp_session.retrbinary("RETR " + file.file_name, temp_file.write)
                            os.utime(temp_local_file, (remote_timestamp, remote_timestamp))
                        except Exception:
                            self.stderr.write(self.style.ERROR(f"ERROR: Unable to retrieve file : {file.file_name}"))
                            return
                else:
                    self.stderr.write(self.style.ERROR(f"ERROR: file does not exist on remote server : {file.file_name}"))
                    return

            ftp_session.close()

            for temp_file_name in os.listdir(temp_dir):
                temp_file_path = os.path.join(temp_dir, temp_file_name)
                local_file_path = os.path.join(BOM_HOME_LOCAL, bom_ftp_directory, temp_file_name)
                
                if temp_file_name.endswith('.nc.gz'):
                    try:
                        subprocess.check_call(["gzip", "-k", "-f", "-q", "-d", temp_file_path])
                        unzipped_file_path = temp_file_path[:-3]
                        
                        shutil.copyfile(temp_file_path, local_file_path)
                        shutil.copyfile(unzipped_file_path, os.path.join(BOM_HOME_LOCAL, bom_ftp_directory, os.path.basename(unzipped_file_path)))
                        
                        os.remove(temp_file_path)
                        os.remove(unzipped_file_path)
                        
                    except subprocess.CalledProcessError:
                        self.stderr.write(self.style.ERROR(f"Unzipping failed for {temp_file_name}"))
                        return
                
                elif temp_file_name.endswith('.nc'):
                    try:
                        shutil.copyfile(temp_file_path, local_file_path)
                        os.remove(temp_file_path)
                    except Exception:
                        self.stderr.write(self.style.ERROR(f"File copy/delete failed for {temp_file_name}"))
                        return
            
            # This block only runs on successful completion
            end_time = datetime.datetime.now()
            duration_seconds = int((end_time - start_time).total_seconds())

            log_entry.completion_time = end_time
            log_entry.duration = duration_seconds
            log_entry.save()
            
            self.stdout.write(self.style.SUCCESS(f"BOM Sync completed successfully in {duration_seconds} seconds."))

        except Exception as e:
            # Any unhandled exceptions will be caught here, but no database update will be made
            self.stderr.write(self.style.ERROR("ERROR running BOM SYNC"))
            self.stderr.write(self.style.ERROR(f"An error occurred: {str(e)}"))
            return