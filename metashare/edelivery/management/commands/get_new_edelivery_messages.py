import logging

from django.core.management.base import BaseCommand, CommandError
from metashare.edelivery.wsdl_services import download_messages
from metashare.settings import LOG_HANDLER

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(LOG_HANDLER)


class Command(BaseCommand):
    def handle(self, *args, **options):
        download_result = download_messages()
        # if success
        if download_result[0]:
            LOGGER.info(download_result[1])
        elif len(download_result) > 2:
            LOGGER.error("{}: {}".format(download_result[1], download_result[2]))
        else:
            LOGGER.info(download_result[1])
