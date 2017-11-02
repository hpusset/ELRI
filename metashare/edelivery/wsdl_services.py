import base64
import logging
import os

import requests
import suds_requests
from django.conf import settings
from lxml import etree
from suds import WebFault
from suds.client import Client

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(settings.LOG_HANDLER)

session = requests.Session()

session.auth = (settings.WSDL_USERNAME, settings.WSDL_PASSWORD)

client = Client(settings.WSDL_URL, transport=suds_requests.RequestsTransport(session))


# local methods
def _admin_xml(message_xml, msg_id):
    """
    Args:
        message_xml: the initial cid:message xml
        msg_id: the message_id of the message_xml

    Returns: A tuple containing the final xml to be dispatched
    to the repository new contributions and the filename to be saved as
    """
    xml_obj = etree.fromstring(message_xml)
    country = xml_obj.find(".//userInfo/country").text
    filename = "{}_{}".format(country, msg_id)
    admin = etree.SubElement(xml_obj, "administration")
    resource_file = etree.SubElement(admin, "resource_file")
    resource_file.text = "{}.xml".format(filename)
    etree.SubElement(admin, "processed").text = "false"
    dataset = etree.SubElement(admin, "dataset")
    dataset_zip = etree.SubElement(dataset, "zip")
    dataset_zip.text = "{}.zip".format(filename)
    etree.SubElement(admin, "edelivery", msg_id=msg_id).text = "true"
    return tuple([etree.tostring(xml_obj, pretty_print=True), filename])


# WSDL services wrappers
def list_pending_messages():
    """
    Wrapper
    WSDL: listPendingMessages(xs:anyType listPendingMessagesRequest, )
    Returns: A list of message ids pending for download
    """
    try:
        return client.service.listPendingMessages()
    except WebFault as ex:
        LOGGER.error(u"{}".format(ex))


def get_message_status(msg_id):
    """
    Args:
        msg_id: Message id

    Returns: Message Status
    """
    # it always returns <empty>
    try:
        return client.service.getStatus(msg_id)
    except WebFault as ex:
        LOGGER.error(u"{}".format(ex))


def download_message(msg_id):
    """
    Wrapper
    WSDL: downloadMessage(max255-non-empty-string messageID, )
    Args:
        msg_id: The id of the message to download

    Returns: True if message is downloaded successfully, False otherwise
    """
    try:
        # Call the service
        data = client.service.downloadMessage(msg_id)

        # Build the desired filename using the payload cid:message which is an xml
        admin_info = None
        destination_path = '{}/unprocessed'.format(settings.CONTRIBUTION_FORM_DATA)
        # Make one iteration to get the xml message (cid: message)
        for p in data.payload:
            if p._payloadId == "cid:message":
                # decode the xml message
                xml_str = base64.b64decode(p.value)
                # update the xml with administration info
                admin_info = _admin_xml(xml_str, msg_id)
                # set the output path
                filename_path = os.path.join(destination_path, admin_info[1])
                break
        # Reiterate to process all payloads
        for p in data.payload:
            if p._payloadId == "cid:message":
                # We already have the final xml from the previous iteration
                output_xml = admin_info[0]

                out = open("{}.xml".format(filename_path), "wb")
                out.write(output_xml)
            else:
                # If not cid:message then it's cid:attachment as zip
                out = open("{}.zip".format(filename_path), "wb")
                out.write(base64.b64decode(p.value))
                out.close()
        return True
    except WebFault as ex:
        code = ex.fault.detail.FaultDetail.code
        message = ex.fault.detail.FaultDetail.message
        LOGGER.error("{}: {}".format(code, message))
        return False


def download_messages():
    """
    Downloads a set of messages if any in list_pending_messages
    Returns: True if all messages have been downloaded successfully,
    False if there are no messages to download or an error has occurred
    during the process
    """
    pending_messages = list_pending_messages()
    if pending_messages:
        for msg in pending_messages:
            # noinspection PyBroadException
            try:
                download_message(msg)
            except Exception as ex:
                return tuple(
                    [False, "There was an error downloading messages from AP", logging.error(ex, exc_info=True)])
        return tuple([True, "New messages successfully downloaded"])
    return tuple([False, "No new messages"])
