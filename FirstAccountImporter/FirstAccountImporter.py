import csv

from beancount.ingest import importer, cache
from beancount.core import data
from beancount.core import flags
from beancount.core.amount import Amount
from beancount.core.number import D

class Importer(importer.ImporterProtocol):
    """Beancount importer for FirstDirect 1st Account CSV"""

    def __init__(self, currentaccount: str):
        self.currentAccount = currentaccount
        self.currency = "GBP"
        self.cachedCSV = None
        self.FLAG = flags.FLAG_WARNING

    def identify(self, file: cache._FileMemo) -> bool:
        if file.mimetype() != 'text/csv':
            return False

        with open(file.name, 'r') as infile:
            header = infile.readline()
            if not header.startswith("Date,Description,Amount,Balance"):
                return False
            return True