from beancount.ingest import importer, cache


class QifImporter(importer.ImporterProtocol):
    """Importer for Qif."""


    def __init__(self):
        # TODO: Add stuff here.


    def identify(self, file: cache._FileMemo):
        if file.mimetype() != 'application/x-qw':
            return False

        #TODO: Add code for caching.
        return True
