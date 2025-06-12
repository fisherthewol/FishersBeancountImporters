import datetime

from beancount.core import flags, data
from beancount.core.amount import Amount, D
from beangulp import importer, cache
from ofxtools.Parser import OFXTree
from ofxtools.Types import OFXSpecError
from ofxtools.models.base import Aggregate


class ofxImporter(importer.ImporterProtocol):
    """Importer for ofx files."""

    def __init__(self, destinationaccount: str, currency: str = 'GBP'):
        self.destinationaccount = destinationaccount
        self.currency = currency
        self.ofxtree = None
        self.FLAG = flags.FLAG_OKAY

    def name(self) -> str:
        return f"ofxImporter.{self.destinationaccount}"

    def identify(self, file: cache._FileMemo) -> bool:
        if not file.name.endswith(".ofx"):
            return False

        try:
            self.ofxtree = self.fileToOfxAggregate(file)
        except OFXSpecError:
            return False

        return True

    def extract(self, file: cache._FileMemo, existing: data.Entries) -> data.Entries:
        if self.ofxtree is None:
            self.ofxtree = self.fileToOfxAggregate(file)

        statement = self.ofxtree.statements[0]
        transactions = statement.transactions
        txns = []
        for idx, transaction in enumerate(transactions):
            meta = data.new_metadata(filename=file.name, lineno=idx)
            amount = Amount(transaction.trnamt, currency=self.currency)
            postings = [data.Posting(
                account=self.destinationaccount,
                units=amount,
                cost=None, price=None, flag=None, meta=None
            )]
            if eurPosting := self.PossibleEURPosting(transaction):
                postings.insert(0, eurPosting)

            txn = data.Transaction(
                meta=meta,
                date=transaction.dtposted,
                flag=self.FLAG,
                payee=transaction.name,
                narration=transaction.memo,
                postings=postings,
                tags=data.EMPTY_SET,
                links=data.EMPTY_SET,
            )
            txns.append(txn)

        return txns

    def file_account(self, file: cache._FileMemo) -> str:
        return self.destinationaccount

    def file_date(self, file: cache._FileMemo):
        return datetime.date.today()

    def PossibleEURPosting(self, transaction) -> data.Posting | None:
        if not transaction.memo.endswith('EUR'):
            return None

        eurAmount = transaction.memo.split(' ')[-2]

        return data.Posting(
            account="REPLACEME",
            units=Amount(D(eurAmount), currency='EUR'),
            price=Amount(-transaction.trnamt, currency=self.currency),
            cost=None, flag=None, meta=None
        )

    @staticmethod
    def fileToOfxAggregate(file: cache._FileMemo) -> Aggregate:
        parser = OFXTree()
        with open(file.name, 'rb') as f:
            parser.parse(f)
        return parser.convert()
