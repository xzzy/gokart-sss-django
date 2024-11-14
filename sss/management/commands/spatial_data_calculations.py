from django.core.management.base import BaseCommand
from sss.models import SpatialDataCalculation
import sss.email as email
from sss import spatial as sss_spatial
import traceback



class Command(BaseCommand):
    help = 'BFRS Spatial Data Calculation Processing'

    def handle(self, *args, **kwargs):
        try:
            imported_spatial_data = SpatialDataCalculation.objects.filter(calculation_status = SpatialDataCalculation.CALCULATION_STATUS[0][0])
            for sd in imported_spatial_data:
                try:
                    sd.calculation_status = SpatialDataCalculation.CALCULATION_STATUS[1][0]
                    sd.save()
                    sss_spatial.spatial(sd)
                    sd.calculation_status = SpatialDataCalculation.CALCULATION_STATUS[2][0]
                    sd.save()
                    try:
                        email.send_success_email(sd)
                        sd.email_sent = True
                        sd.save()
                    except Exception as e:
                        print(f"Error in Sending Success email for {sd.bfrs}")
                    print(f"Calculation Completed: {sd.bfrs}")
                except Exception as e:
                    sd.calculation_status = SpatialDataCalculation.CALCULATION_STATUS[3][0]
                    sd.error = traceback.format_exc()
                    sd.save()
                    try:
                        email.send_failure_email(sd)
                        sd.email_sent = True
                        sd.save()
                    except Exception as e:
                        print(traceback.format_exc())
                        print(f"Error in Sending Failure email for {sd.bfrs}")
                    print(f"Calculation Error: {sd.bfrs}")

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred: {str(e)}"))
            print (e)
