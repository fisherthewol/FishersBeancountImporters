import datetime

from beancount.core import flags, data
from beancount.core.amount import Amount
from beancount.core.number import D
from beancount.ingest import importer, cache
from quiffen import Qif, AccountType, Transaction, ParserException


class QifImporter(importer.ImporterProtocol):
    """Importer for Qif Files."""

    def __init__(self,
                 destinationaccount: str,
                 dayfirst: bool,
                 qifaccount: str = '',
                 currency: str = 'GBP'):
        self.qifObject = None
        self.destinationAccount = destinationaccount
        self.dayFirst = dayfirst
        self.qifAccount = qifaccount
        self.currency = currency
        self.FLAG = flags.FLAG_OKAY

    def name(self):
        return f"QifImporter.{self.destinationAccount}"

    def identify(self, file: cache._FileMemo):
        if not file.name.endswith('.qif'):
            return False

        try:
            self.qifObject = Qif.parse(file.name, day_first=self.dayFirst)
        except ParserException:
            return False

        return True

    def extract(self, file, existing_entries=None):
        if self.qifObject is None:
            self.qifObject = Qif.parse(file.name, day_first=self.dayFirst)

        account = self.GetQifAccount()

        if len(account.transactions) != 1:
            print('More than one "transaction" in account.transactions, aborting.')
            return []
        (accounttype, transactionlist), = account.transactions.items()

        match accounttype:
            case AccountType.CASH | AccountType.BANK:
                invertSign = False
            case AccountType.CREDIT_CARD:
                invertSign = True
            case _:
                print(f'Unknown account type: {account.account_type}')
                return []

        txns = []
        for transaction in transactionlist:
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

    @staticmethod
    def GetNarration(transaction: Transaction):
        narrations = []
        if transaction.memo:
            narrations.append(f'Memo: {transaction.memo}')
        if transaction.cleared:
            narrations.append(f'Cleared: {transaction.cleared}')
        if transaction.category:
            narrations.append(f'Category: {transaction.category}')
        if transaction.check_number:
            narrations.append(f'Check Number: {transaction.check_number}')

        if len(narrations) == 0:
            return None

        return ', '.join(narrations)

    def GetQifAccount(self):
        if len(self.qifObject.accounts) != 1:
            try:
                return self.qifObject.accounts[self.qifAccount]
            except KeyError:
                print(f'Number of accounts > 1 and specified account ({self.qifAccount}) not found.')
                return []
        else:
            try:
                return self.qifObject.accounts[self.qifAccount] if self.qifAccount else self.qifObject.accounts[
                    'Quiffen Default Account']
            except KeyError:
                print(f'Number of accounts = 1 and specified account ({self.qifAccount}) or default account not found.')
                return []
