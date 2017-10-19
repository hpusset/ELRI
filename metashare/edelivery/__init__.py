from suds.client import Client
import requests
import suds_requests
from django.conf import settings

session = requests.Session()

session.auth = (settings.WSDL_USERNAME, settings.WSDL_PASSWORD)

client = Client(settings.WSDL_URL, transport=suds_requests.RequestsTransport(session))