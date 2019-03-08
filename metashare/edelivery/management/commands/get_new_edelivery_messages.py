import logging

from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from metashare.edelivery.wsdl_services import download_messages
from metashare.settings import LOG_HANDLER, CONTRIBUTIONS_ALERT_EMAILS

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(LOG_HANDLER)


class Command(BaseCommand):
    def handle(self, *args, **options):
        download_result = download_messages()
        # if success
        if download_result[0]:
            LOGGER.info(download_result[1])

            #contact the superusers of the NRS
            superuser_emails = User.objects.filter(is_superuser=True).values_list('email', flat=True)
            try:
                send_mail(_("New contributions through eDelivery"),
                          _("You have new unmanaged contributed resources on elri.eu, through eDelivery."),
                          recipient_list=superuser_emails,
                          from_email='no-reply@elri.eu', \
                          fail_silently=False)
            except:
                LOGGER.error(_("An error has occurred while trying to send email to contributions alert recipients."))

        elif len(download_result) > 2:
            LOGGER.error("{}: {}".format(download_result[1], download_result[2]))
        else:
            LOGGER.info(download_result[1])
