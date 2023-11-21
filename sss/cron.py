from django_cron import CronJobBase, Schedule
import logging
from django.core import management

#logging
log = logging.getLogger(__name__)


class FetchCatalogueDataCronJob(CronJobBase):
    RUN_EVERY_MINS = 10

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'sss.cron.fetch_and_cache_catalogue_data'

    def do(self):
        log.info("CRON JOB: fetching catalogue data...")

        management.call_command("fetch_and_cache_catalogue_data")

class FetchBfrsRegionDataCronJob(CronJobBase):
    RUN_EVERY_MINS = 10

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'sss.cron.fetch_and_cache_bfrs_region_data'

    def do(self):
        log.info("CRON JOB: fetching bfrs region data...")

        management.call_command("fetch_and_cache_bfrs_region_data")


class SyncBOMDataCronJob(CronJobBase):
    RUN_EVERY_MINS = 30

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'sss.cron.sync_bom_data'

    def do(self):
        log.info("CRON JOB: syncing bom data...")

        management.call_command("sync_ftp_bom")        