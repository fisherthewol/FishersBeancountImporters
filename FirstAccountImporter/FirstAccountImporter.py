from beancount.ingest import importer, cache
from beancount.core import data
from beancount.core import flags
from beancount.core.amount import Amount
from beancount.core.number import D

class Importer(importer.ImporterProtocol):
