import datetime

from beancount.core import flags, data
from beancount.core.amount import Amount
from beancount.core.number import D
from beancount.ingest import importer, cache
from quiffen import Qif, AccountType


class QifImporter(importer.ImporterProtocol):
    """Importer for Qif Files."""

    def __init__(self,
                 destinationaccount: str,
                 dayfirst: bool,
                 qifaccount: str = '',
                 currency: str = 'GBP'):
        self.destinationAccount = destinationaccount
        self.dayFirst = dayfirst
        self.qifAccount = qifaccount
        self.currency = currency
        self.FLAG = flags.FLAG_OKAY

    def name(self):
        return f"QifImporter.{self.destinationAccount}"

    def identify(self, file: cache._FileMemo):
        if file.mimetype() != 'application/x-qw':
            return False

        # TODO: Add code for caching.
        return True

    def extract(self, file, existing_entries=None):
        parsedQif = Qif.parse(file.name, day_first=self.dayFirst)
        if len(parsedQif.accounts) != 1:
            try:
                account = parsedQif.accounts[self.qifAccount]
            except KeyError:
                print(f'Number of accounts > 1 and specified account ({self.qifAccount}) not found.')
                return []
        else:
            try:
                account = parsedQif.accounts[self.qifAccount] if self.qifAccount else parsedQif.accounts[
                    'Quiffen Default Account']
            except KeyError:
                print(f'Number of accounts = 1 and specified account ({self.qifAccount}) or default account not found.')
                return []

        transactions = account.transactions[account.account_type]
        match account.account_type:
            case AccountType.CASH | AccountType.BANK:
                invertSign = False
            case AccountType.CREDIT_CARD:
                invertSign = True
            case _:
                print(f'Unknown account type: {account.account_type}')
                return []

        txns = []
        for transaction in transactions:
            meta = data.new_metadata(filename=file.name, lineno=transaction.line_number)
            amount = Amount(-D(transaction.amount), currency=self.currency) if invertSign else Amount(
                D(transaction.amount), currency=self.currency)
            postings = [data.Posting(
                account=self.destinationAccount,
                units=amount,
                cost=None, price=None, flag=None, meta=None
            )]
            txn = data.Transaction(
                meta=meta,
                date=transaction.date,
                flag=self.FLAG,
                payee=transaction.payee.rstrip(),
                narration=self.GetNarration(transaction),
                postings=postings,
                tags=data.EMPTY_SET,
                links=data.EMPTY_SET
            )
            txns.append(txn)

        return txns

    def file_account(self, file: cache._FileMemo):
        return self.destinationAccount

    def file_date(self, file: cache._FileMemo):
        return datetime.date.today()

    def GetNarration(self, transaction):
        # TODO: Implement this based on other quiffen attributes.
        return ''
