from PyPDF2 import PdfReader
from beancount.ingest import importer, cache


def pdf_to_text(filename: str):
    """Convert pdf file to text."""
    reader = PdfReader(filename)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


class Importer(importer.ImporterProtocol):
    """A Beancount importer for Access UK Payslips."""

    def __init__(self, incomeaccount: str, checkingaccount: str):
        self.incomeAccount = incomeaccount
        self.checkingAccount = checkingaccount
        self.currency = "GBP"
        self.cachedPDF = None

    def identify(self, file: cache._FileMemo) -> bool:
        if file.mimetype() != 'application/pdf':
            return False

        self.cachedPDF = file.convert(pdf_to_text)
        if self.cachedPDF:
            return "ACCESS UK" in self.cachedPDF

        return False
