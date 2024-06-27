import datetime

from pypdf import PdfReader
from beancount.ingest import importer, cache
from beancount.core import data
from beancount.core import flags
from beancount.core.amount import Amount
from beancount.core.number import D


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
            currentaccount: str,
            paye: str,
            pensionmatchaccount: str,
            nationalinsuranceaccount: str,
            pensionassetaccount: str,
            studentloanaccount: str,
            y2kfix: str,
            flag: str = ''):
        """
        Initialise and importer for Access UK Payslips
        :param studentloanaccount:
        :param salaryaccount: Account to book income from.
        :param currentaccount: Account receiving your Net Pay.
        :param paye: Account to book PAYE tax to.
        :param pensionmatchaccount: Pension Match from Access.
        :param nationalinsuranceaccount: NI Tax account.
        :param pensionassetaccount: Account to contribute pension to.
        :param studentloanaccount: Account for student loan balance.

        :param y2kfix: First 2 digits of year for date (Payslip has y2k bug).
        """
        self.salaryAccount = salaryaccount
        self.currentAccount = currentaccount
        self.PAYE = paye
        self.pensionMatch = pensionmatchaccount
        self.NIAccount = nationalinsuranceaccount
        self.PensionAccount = pensionassetaccount
        self.StudentLoanAccount = studentloanaccount
        self.currency = "GBP"
        self.cachedPDF: str = None
        self.y2kFix = y2kfix
        self.FLAG = flags.FLAG_WARNING if flag == '' else flags.FLAG_OKAY

    def identify(self, file: cache._FileMemo) -> bool:
        """Check that is a PDF containing the text "Pay" and "ACCESS UK" """
        if file.mimetype() != 'application/pdf':
            return False

        self.cachedPDF = file.convert(pdf_to_text)
        if self.cachedPDF:
            return "PAY" in self.cachedPDF and "ACCESS UK" in self.cachedPDF

        return False

    def extract(self, file: cache._FileMemo, existing_entries=None):
        # Check for text of pdf
        if self.cachedPDF is None:
            self.cachedPDF = file.convert(pdf_to_text)
        # Split into lines.
        lines = self.cachedPDF.splitlines()

        # Determine values for each posting.
        netpay = list(
            filter(
                lambda line: line.startswith("Net Pay"),
                lines
            )
        )[0].split(' ')[3]
        salary = list(
            filter(
                lambda line: line.startswith("Basic Salary"),
                lines
            )
        )[0].split(' ')[2]
        pension_single = list(
            filter(
                lambda line: line.startswith("AEGON GPPP"),
                lines
            )
        )[0].split(' ')[3]
        paye_tax = list(
            filter(
                lambda line: line.startswith("PAYE"),
                lines
            )
        )[0].split(' ')[1]
        national_insurance = list(
            filter(
                lambda line: line.startswith("Employee NI"),
                lines
            )
        )[1].split(' ')[2]
        student_loan = list(
            filter(
                lambda line: line.startswith("Student Loan Plan 2"),
                lines
            )
        )[0].split(' ')[4]

        meta = data.new_metadata(file.name, 0)
        meta['date']: datetime.date = self.file_date(file)

        postings = [
            data.Posting(
                account=self.currentAccount,
                units=Amount(D(netpay), self.currency),
                cost=None, price=None, flag=None, meta=None
            ),
            data.Posting(
                account=self.StudentLoanAccount,
                units=Amount(D(student_loan), self.currency),
                cost=None, price=None, flag=None, meta=None
            ),
            data.Posting(
                account=self.PAYE,
                units=Amount(D(paye_tax), self.currency),
                cost=None, price=None, flag=None, meta=None
            ),
            data.Posting(
                account=self.NIAccount,
                units=Amount(D(national_insurance), self.currency),
                cost=None, price=None, flag=None, meta=None
            ),
            data.Posting(
                account=self.PensionAccount,
                units=Amount(-D(pension_single) * 2, self.currency),
                cost=None, price=None, flag=None, meta=None
            ),
            data.Posting(
                account=self.pensionMatch,
                units=Amount(D(pension_single), self.currency),
                cost=None, price=None, flag=None, meta=None
            ),
            data.Posting(
                account=self.salaryAccount,
                units=Amount(-D(salary), self.currency),
                cost=None, price=None, flag=None, meta=None
            )
        ]
        txn = data.Transaction(
            meta=meta,
            date=self.file_date(file),
            flag=self.FLAG,
            payee="SELF",
            narration=f"Paycheck {meta['date'].day} {meta['date'].month} {meta['date'].year}",
            postings=postings,
            tags=data.EMPTY_SET,
            links=data.EMPTY_SET
        )

        return [txn]

    def file_account(self, file: cache._FileMemo) -> str:
        return self.salaryAccount

    def file_date(self, file: cache._FileMemo):
        """Date is of format DD-MON-YY"""
        # Ensure that there is cached version of the file.
        if self.cachedPDF is None:
            self.cachedPDF = file.convert(pdf_to_text)

        datelines = self.cachedPDF.splitlines()
        dateparts = list(filter(lambda line: line.startswith("Payslip Date:"), datelines))[0].split(' ')[2].split('-')
        year = self.y2kFix + dateparts[2]
        month = tri_to_month[dateparts[1]]
        return datetime.date(int(year), int(month), int(dateparts[0]))
