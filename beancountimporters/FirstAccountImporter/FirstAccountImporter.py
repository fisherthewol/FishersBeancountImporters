import collections
import csv
import datetime

from beancount.ingest import importer, cache
from beancount.core import data
from beancount.core import flags
from beancount.core.amount import Amount
from beancount.core.number import D


def csv_to_list(filename: str):
    with open(filename, 'r') as infile:
        rows: [str] = infile.readlines()
    return rows


class Importer(importer.ImporterProtocol):
    """Beancount importer for FirstDirect 1st Account CSV"""

    def __init__(self, currentaccount: str, flag: str = ''):
        self.currentAccount = currentaccount
        self.currency = "GBP"
        self.FLAG = flags.FLAG_WARNING if flag == '' else flags.FLAG_OKAY
        self.cachedRows: [str] = None

    def identify(self, file: cache._FileMemo) -> bool:
        if file.mimetype() != 'text/csv':
            return False

        self.cachedRows = file.convert(csv_to_list)
        if self.cachedRows:
            return self.cachedRows[0].startswith("Date,Description,Amount,Balance")

        return False

    def extract(self, file, existing_entries=None):
        if self.cachedRows is None:
            self.cachedRows = file.convert(csv_to_list)

        rows = csv.DictReader(self.cachedRows)
        txns = collections.deque()
        finalBalance = None

        for idx, row in enumerate(rows):
            meta = data.new_metadata(file.name, idx + 1)
            postings = [data.Posting(
                account=self.currentAccount,
                units=Amount(D(row['Amount']), self.currency),
                cost=None, price=None, flag=None, meta=None
            )]
            splitdate = row['Date'].split('/')
            d = splitdate[0]
            m = splitdate[1]
            y = splitdate[2]
            newdate = datetime.date(int(y), int(m), int(d))
            txn = data.Transaction(
                meta=meta,
                date=newdate,
                flag=self.FLAG,
                payee=None,
                narration=row['Description'],
                postings=postings,
                tags=data.EMPTY_SET,
                links=data.EMPTY_SET
            )
            # Most Recent item is first in CSV, and we want it to be last; add to left.
            txns.appendleft(txn)
            if idx == 0:
                finalBalance = (newdate, idx + 1, row['Balance'])

        if finalBalance is not None:
            balanceDirective = data.Balance(
                meta=data.new_metadata(file.name, finalBalance[1], kvlist={'date': self.file_date(file)}),
                date=finalBalance[0],
                account=self.currentAccount,
                amount=Amount(D(finalBalance[2]), self.currency),
                diff_amount=None, tolerance=None
            )
            txns.append(balanceDirective)

        return list(txns)

    def file_account(self, file):
        return self.currentAccount

    def file_date(self, file):
        return datetime.date.today()


