from beancount.core import flags
from beangulp import importer, cache
from ofxtools.Types import OFXSpecError
from ofxtools.Parser import OFXTree

class ofxImporter(importer.ImporterProtocol):
    """Importer for ofx files."""

    def __init__(self, destinationaccount: str, currency: str = 'GBP'):
        self.destinationaccount = destinationaccount
        self.currency = currency
        self.ofxtree = None
        self.FLAG = flags.FLAG_OKAY

    def name(self) -> str:
        return f"ofxImporter.{self.destinationaccount}"

    def identify(self, file: cache._FileMemo) -> bool:
        if not file.name.endswith(".ofx"):
            return False

        try:
            parser = OFXTree()
            with open(file.name, 'rb') as f:
                parser.parse(f)
            self.ofxtree = parser.convert()
        except OFXSpecError:
            return False

        return True