from beancount.ingest import importer


class AccessSalaryImporter(importer.ImporterProtocol):

    def __init__(self, incomeaccount: str, checkingaccount: str):
        self.incomeAccount = incomeaccount
        self.checkingAccount = checkingaccount
        self.currency = "GBP"

    def identify(self, file):
        raise NotImplementedError("Not Implemented")
