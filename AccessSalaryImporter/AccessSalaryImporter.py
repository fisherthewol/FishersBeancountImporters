import datetime

from PyPDF2 import PdfReader
from beancount.ingest import importer, cache
from beancount.core import data
from beancount.core import flags
from beancount.core.amount import Amount
from beancount.core.number import ZERO, D
from beancount.ingest.importers.mixins import filing, identifier
from beancount.utils.date_utils import parse_date_liberally


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
            salaryaccount: str,
            checkingaccount: str,
            y2kfix: str):
        """Initialise importer.
        :parameter salaryaccount Account to book income into.
        :parameter checkingaccount Account receiving income.
        :parameter y2kfix First 2 digits of year for date (Payslip has y2k bug).
        """
        self.salaryAccount = salaryaccount
        self.checkingAccount = checkingaccount
        self.currency = "GBP"
        self.cachedPDF: str = None
        self.y2kFix = y2kfix
        self.FLAG = flags.FLAG_WARNING

    def identify(self, file: cache._FileMemo) -> bool:
        """Check that is a PDF containing the text "Pay" and "ACCESS UK" """
        if file.mimetype() != 'application/pdf':
            return False

        self.cachedPDF = file.convert(pdf_to_text)
        if self.cachedPDF:
            return "PAY" in self.cachedPDF and "ACCESS UK" in self.cachedPDF

        return False

    def extract(self, file, existing_entries=None):
        # Check for text of pdf
        if self.cachedPDF is None:
            self.cachedPDF = file.convert(pdf_to_text)
        # Split into lines.
        lines = self.cachedPDF.splitlines()

        # Determine values for each posting.
        netpay = list(
            filter(
                lambda line: line.startswith("Net Pay"),
                lines))[0].split(' ')[3]
        salary = list(
            filter(
                lambda line: line.startswith("Basic Salary"),
                lines))[0].split(' ')[2]
        pensionSingle = list(
            filter(
                lambda line: line.startswith("AEGON GPPP"),
                lines))[0].split(' ')[3]
        nationalInsurance = list(
            filter(
                lambda line: line.startswith("Employee NI"),
                lines))[0].split(' ')[2]

        meta = data.new_metadata(file.name, 0)
        meta['date']: datetime.date = self.file_date(file)

        postings = [
            data.Posting(
                account=self.checkingAccount,
                units=Amount()
            )
        ]
        txn = data.Transaction(
            meta=meta,
            date=self.file_date(file),
            flag=self.FLAG,
            payee="SELF",
            narration=f"Paycheck {meta['date'].day} {meta['date'].month} {meta['date'].year}",
            postings=postings
        )

        return [txn]

    def file_account(self, file):
        return self.salaryAccount

    def file_date(self, file):
        """Date is of format DD-MON-YY"""
        # Ensure that there is cached version of the file.
        if self.cachedPDF is None:
            self.cachedPDF = file.convert(pdf_to_text)

        datelines = self.cachedPDF.splitlines()
        for line in datelines:
            if line.startswith("Payslip Date:"):
                dateparts = line.split(' ')[2].split('-')
                year = self.y2kFix + dateparts[2]
                month = tri_to_month[dateparts[1]]
                return datetime.date(int(year), int(month), int(dateparts[0]))
