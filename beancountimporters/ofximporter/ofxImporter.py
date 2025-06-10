from beancount.core import flags
from beangulp import importer

class ofxImporter(importer.ImporterProtocol):
    """Importer for ofx files."""

    def __init__(self, destinationaccount: str, currency: str = 'GBP'):
        self.destinationaccount = destinationaccount
        self.currency = currency
        self.FLAG = flags.FLAG_OKAY

    def name(self) -> str:
        return f"ofxImporter.{self.destinationaccount}"