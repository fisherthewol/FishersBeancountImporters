import datetime

from PyPDF2 import PdfReader
from beancount.ingest import importer, cache


def pdf_to_text(filename: str):
    """Convert pdf file to text."""
    reader = PdfReader(filename)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

tri_to_month = {
    "JAN": "01",
    "FEB": "02",
    "MAR": "03",
    "APR": "04",
    "MAY": "05",
    "JUN": "06",
    "JUL": "07",
    "AUG": "08",
    "SEP": "09",
    "OCT": "10",
    "NOV": "11",
    "DEC": "12",
}


class Importer(importer.ImporterProtocol):
    """A Beancount importer for Access UK Payslips."""

    def __init__(
            self,
            incomeaccount: str,
            checkingaccount: str,
            y2kfix: str):
        self.incomeAccount = incomeaccount
        self.checkingAccount = checkingaccount
        self.currency = "GBP"
        self.cachedPDF: str = None
        self.y2kFix = y2kfix

    def identify(self, file: cache._FileMemo) -> bool:
        """Check that is a PDF containing the text "Pay" and "ACCESS UK" """
        if file.mimetype() != 'application/pdf':
            return False

        self.cachedPDF = file.convert(pdf_to_text)
        if self.cachedPDF:
            return "PAY" in self.cachedPDF and "ACCESS UK" in self.cachedPDF

        return False

    def file_account(self, file): return self.incomeAccount

    def file_date(self, file):
        # Ensure that there is cached version of the file.
        if self.cachedPDF is None:
            self.cachedPDF = file.convert(pdf_to_text)

        datelines = self.cachedPDF.split('\n')  # Split into lines.
        for line in datelines:
            if line.startswith("Payslip Date:"):
                dateparts = line.split(' ')[1].split('-')
                year = self.y2kFix + dateparts[2]
                month = tri_to_month[dateparts[1]]
                return datetime.date(int(year), int(month), int(dateparts[0]))
