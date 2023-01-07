from beancount.ingest import importer, cache


class AccessSalaryImporter(importer.ImporterProtocol):
    """A Beancount importer for Access UK Payslips."""

    def __init__(self, incomeaccount: str, checkingaccount: str):
        self.incomeAccount = incomeaccount
        self.checkingAccount = checkingaccount
        self.currency = "GBP"

    def identify(self, file: cache._FileMemo):
        if file.mimetype() != 'application/pdf':
            return False
        raise NotImplementedError("Not Implemented")
