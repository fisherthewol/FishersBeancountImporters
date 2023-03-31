import collections
import csv
import datetime

from beancount.ingest import importer, cache
from beancount.core import data
from beancount.core import flags
from beancount.core.amount import Amount
from beancount.core.number import D


class Importer(importer.ImporterProtocol):
    """Beancount importer for FirstDirect 1st Account CSV"""

    def __init__(self, currentaccount: str):
        self.currentAccount = currentaccount
        self.currency = "GBP"
        self.FLAG = flags.FLAG_WARNING

    def identify(self, file: cache._FileMemo) -> bool:
        if file.mimetype() != 'text/csv':
            return False

        with open(file.name, 'r') as infile:
            header = infile.readline()
            if not header.startswith("Date,Description,Amount,Balance"):
                return False

        return True

    def extract(self, file, existing_entries=None):
        with open(file.name, newline='') as infile:
            rows = csv.DictReader(infile)

            txns = collections.deque()
            finalBalance = None

            for idx, row in enumerate(rows):
                meta = data.new_metadata(file.name, idx + 1, kvlist={'date': self.file_date(file)})
                posting = data.Posting(
                    account=self.currentAccount,
                    units=Amount(D(row['Amount']), self.currency),
                    cost=None, price=None, flag=None, meta=None
                )
                d = row['Date'].split('/')[0]
                m = row['Date'].split('/')[1]
                y = row['Date'].split('/')[2]
                newdate = datetime.date(int(y), int(m), int(d))
                txn = data.Transaction(
                    meta=meta,
                    date=newdate,
                    flag=self.FLAG,
                    payee=None,
                    narration=row['Description'],
                    postings=[posting],
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
