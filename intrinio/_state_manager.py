import os
import datetime
import xml.etree.ElementTree as ET
from requests import Session

from local_settings import INTRINIO_USERNAME, INTRINIO_PASSWORD

REQUEST_LIMIT = 499


def get_request_state_path():
    return os.path.join(os.path.dirname(__file__), "data/request_state.xml")


class State(object):

    def __enter__(self):
        self.session = Session()
        self.session.auth = (INTRINIO_USERNAME, INTRINIO_PASSWORD)

        self._tree = ET.parse(get_request_state_path())
        root = self._tree.getroot()

        if datetime.date.today().isoformat() == str(root.find("ActiveDate").get("value")):
            self._count = int(root.find("RequestCount").get("value"))
        else:
            self._count = 0
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        root = self._tree.getroot()
        root.find("RequestCount").set("value", str(self._count))
        root.find("ActiveDate").set("value", datetime.date.today().isoformat())
        self._tree.write(get_request_state_path())
        self.session.close()

    def increment_request_count(self):
        self._count = self._count + 1
        if self._count > REQUEST_LIMIT:
            raise Exception("request limit reached")

    def is_under_request_limit(self):
        return self._count < (REQUEST_LIMIT - 1)

    def get_last_ticker_index(self):
        return int(self._tree.getroot().find("LastTicker").get("value"))

    def set_last_ticker_index(self, index):
        self._tree.getroot().find("LastTicker").set("value", str(index))
