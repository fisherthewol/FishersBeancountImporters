import collections
import csv
import datetime

from beancount.core import flags, data
from beancount.core.amount import Amount
from beancount.core.number import D
from beancount.ingest import importer, cache


def csv_to_list(filename: str):
    with open(filename, 'r') as infile:
        rows: [str] = infile.readlines()
    return rows


class Importer(importer.ImporterProtocol):
    """Imports Amex CSVs"""

    def __init__(self, creditcardaccount: str, flag: str = ''):
        self.creditCardAccount = creditcardaccount
        self.currency = "GBP"
        self.FLAG = flags.FLAG_WARNING if flag == '' else flags.FLAG_OKAY
        self.cachedRows = None

    def identify(self, file: cache._FileMemo) -> bool:
        if file.mimetype() != 'text/csv':
            return False

        self.cachedRows = file.convert(csv_to_list)
        if self.cachedRows:
            return self.cachedRows[0].startswith("Date,Description,Amount,Extended Details,Appears On Your Statement "
                                                 "As,Address,Town/City,Postcode,Country,Reference,Category")

        return False

    def extract(self, file, existing_entries=None):
        if self.cachedRows is None:
            self.cachedRows = file.convert(csv_to_list)

        rows = csv.DictReader(self.cachedRows)
        txns = []

        for idx, row in enumerate(rows):
            meta = data.new_metadata(file.name, idx + 1, kvlist={'reference': row['Reference']})
            posting = data.Posting(
                account=self.creditCardAccount,
                units=Amount(-D(row['Amount']), self.currency),
                cost=None, price=None, flag=None, meta=None
            )
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
                postings=[posting],
                tags=data.EMPTY_SET,
                links=data.EMPTY_SET
            )
            txns.append(txn)

        return txns

    def file_account(self, file):
        return self.creditCardAccount

    def file_date(self, file):
        return datetime.date.today()
