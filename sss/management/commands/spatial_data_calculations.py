from django.core.management.base import BaseCommand
from sss.models import SpatialDataCalculation, ManagementCommandStatus
import sss.email as email
from sss import spatial as sss_spatial
import traceback
import datetime


class Command(BaseCommand):
    help = 'BFRS Spatial Data Calculation Processing'
    command_name = 'spatial_data_calculations'

    def handle(self, *args, **kwargs):
        start_time = datetime.datetime.now()
        self.stdout.write(f"{start_time} : Starting Spatial Data Calculations")

        try:
            log_entry, created = ManagementCommandStatus.objects.get_or_create(
                command=self.command_name
            )
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to access database for command status: {e}"))
            return

        try:
            imported_spatial_data = SpatialDataCalculation.objects.filter(
                calculation_status=SpatialDataCalculation.CALCULATION_STATUS[0][0]
            )
            
            for sd in imported_spatial_data:
                try:
                    self.stdout.write(f"Processing: {sd.bfrs}")
                    
                    # 1. Start Calculation
                    sd.calculation_status = SpatialDataCalculation.CALCULATION_STATUS[1][0]
                    sd.save()
                    sss_spatial.spatial(sd)
                    
                    # 2. Calculation Success
                    sd.calculation_status = SpatialDataCalculation.CALCULATION_STATUS[2][0]
                    sd.save()
                    
                    # 3. Send Success Email
                    try:
                        email.send_success_email(sd)
                        sd.email_sent = True
                        sd.save()
                    except Exception as e:
                        self.stdout.write(f"Error in Sending Success email for {sd.bfrs}: {e}")
                        
                    self.stdout.write(f"Calculation Completed: {sd.bfrs}")
                    
                except Exception:
                    # Individual SpatialDataCalculation processing failed
                    sd.calculation_status = SpatialDataCalculation.CALCULATION_STATUS[3][0]
                    sd.error = traceback.format_exc()
                    sd.save()
                    
                    # Send Failure Email
                    try:
                        email.send_failure_email(sd)
                        sd.email_sent = True
                        sd.save()
                    except Exception as e:
                        self.stdout.write(f"Error in Sending Failure email for {sd.bfrs}: {e}")
                        self.stderr.write(self.style.ERROR(traceback.format_exc()))
                        
                    self.stdout.write(f"Calculation Error: {sd.bfrs}")

            end_time = datetime.datetime.now()
            duration_seconds = int((end_time - start_time).total_seconds())

            log_entry.completion_time = end_time
            log_entry.duration = duration_seconds
            log_entry.save()
            
            self.stdout.write(self.style.SUCCESS(f"Spatial Data Calculations completed successfully in {duration_seconds} seconds."))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"FATAL ERROR running {self.command_name}: {e}"))
            self.stderr.write(self.style.ERROR(traceback.format_exc()))