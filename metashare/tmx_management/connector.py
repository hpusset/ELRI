import os

from BaseXClient import BaseXClient
from settings import BASEX_DB, BASEX_PASSWORD, BASEX_SERVER_PORT, BASEX_SERVER_URL, BASEX_USER


def connect(db):
    session = BaseXClient.Session(BASEX_SERVER_URL, BASEX_SERVER_PORT, BASEX_USER, BASEX_PASSWORD)
    if not db:
        session.execute("OPEN {}".format(BASEX_DB))
    else:
        session.execute("OPEN {}".format(db))
    return session
