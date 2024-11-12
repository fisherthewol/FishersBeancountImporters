import collections
import csv
import datetime

from beancount.core import flags, data
from beancount.core.amount import Amount
from beancount.core.number import D
from beancount.ingest import importer, cache

from ..Heuristics.CSVHeuristics import CSVHeuristics


def csv_to_list(filename: str):
    with open(filename, 'r', newline='') as infile:
        rows: [str] = infile.readlines()
    return rows


class Importer(importer.ImporterProtocol):
    """Imports HSBC CSVs"""

    def __init__(self, creditcardaccount: str, groceriesaccount: str, phoneaccount: str, flag: str = ''):
        self.creditCardAccount = creditcardaccount
        self.currency = "GBP"
        self.FLAG = flags.FLAG_WARNING if flag == '' else flags.FLAG_OKAY
        self.heuristics = CSVHeuristics(
            payeecolumn=1,
            valuecolumn=2,
            currency=self.currency,
            groceriesaccount=groceriesaccount,
            phoneaccount=phoneaccount,
            invertvalue=True)

    def identify(self, file: cache._FileMemo) -> bool:
        if file.mimetype() != 'text/csv':
            return False

        self.cachedRows = file.convert(csv_to_list)
        return True

    def extract(self, file, existing_entries=None):
        if self.cachedRows is None:
            self.cachedRows = file.convert(csv_to_list)

        rows = csv.reader(self.cachedRows)
        txns = []

        for idx, row in enumerate(rows):
            meta = data.new_metadata(file.name, idx + 1)
            postings = [data.Posting(
                account=self.creditCardAccount,
                units=Amount(D(row[2]), self.currency),
                cost=None, price=None, flag=None, meta=None
            )]
            if (identified := self.heuristics.identify(row)) is not None:
                postings.append(identified)
            splitdate = row[0].split('/')
            d = splitdate[0]
            m = splitdate[1]
            y = splitdate[2]
            newdate = datetime.date(int(y), int(m), int(d))
            txn = data.Transaction(
                meta=meta,
                date=newdate,
                flag=self.FLAG,
                payee=row[1],
                narration=row[1],
                postings=postings,
                tags=data.EMPTY_SET,
                links=data.EMPTY_SET
            )
            txns.append(txn)

        return txns

    def file_account(self, file):
        return self.creditCardAccount

    def file_date(self, file):
        return datetime.date.today()
