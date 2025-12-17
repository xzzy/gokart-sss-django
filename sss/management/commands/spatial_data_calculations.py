from django.core.management.base import BaseCommand
from sss.models import SpatialDataCalculation, ManagementCommandStatus
import sss.email as email
from sss import spatial as sss_spatial
import traceback
from django.utils import timezone
import logging

logger = logging.getLogger('cron_tasks')


class Command(BaseCommand):
    help = 'BFRS Spatial Data Calculation Processing'
    command_name = 'spatial_data_calculations'

    def handle(self, *args, **kwargs):
        start_time = timezone.now()
        logger.info("Starting Spatial Data Calculations")

        try:
            log_entry, created = ManagementCommandStatus.objects.get_or_create(
                command=self.command_name
            )
        except Exception as e:
            logger.error(f"Failed to access database for command status: {e}")
            return

        try:
            imported_spatial_data = SpatialDataCalculation.objects.filter(
                calculation_status=SpatialDataCalculation.CALCULATION_STATUS[0][0]
            )
            
            for sd in imported_spatial_data:
                try:
                    logger.info(f"Processing: {sd.bfrs}")
                    
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
                        logger.info(f"Error in Sending Success email for {sd.bfrs}: {e}")
                        
                    logger.info(f"Calculation Completed: {sd.bfrs}")
                    
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
                        logger.error(f"Error in Sending Failure email for {sd.bfrs}: {e}")
                        logger.error(traceback.format_exc())
                        
                    logger.info(f"Calculation Error: {sd.bfrs}")

            end_time = timezone.now()
            duration_seconds = int((end_time - start_time).total_seconds())

            log_entry.completion_time = end_time
            log_entry.duration = duration_seconds
            log_entry.save()
            
            logger.info(f"Spatial Data Calculations completed successfully in {duration_seconds} seconds.")

        except Exception as e:
            logger.error(f"FATAL ERROR running {self.command_name}: {e}")
            logger.error(traceback.format_exc())