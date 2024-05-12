import datetime
from typing import Optional

from beancount.core import flags, data
from beancount.core.amount import Amount
from beancount.core.number import D
from beancount.ingest import importer, cache
from quiffen import Qif, AccountType, Transaction, ParserException, Account


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

    def name(self) -> str:
        return f'QifImporter.{self.destinationAccount}'

    def identify(self, file: cache._FileMemo) -> bool:
        if not file.name.endswith('.qif'):
            return False

        try:
            self.qifObject = Qif.parse(file.name, day_first=self.dayFirst)
        except ParserException:
            return False

        return True

    def extract(self, file: cache._FileMemo, existing_entries=None) -> list[data.Transaction]:
        if self.qifObject is None:
            self.qifObject = Qif.parse(file.name, day_first=self.dayFirst)

        account = self.GetQifAccount()
        if not account:
            return []

        if len(account.transactions) != 1:
            print('More than one "transaction" in account.transactions, aborting.')
            return []
        (accounttype, transactionlist), = account.transactions.items()

        invertSign = self.GetInvertSign(accounttype)
        if invertSign is None:
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

    def file_account(self, file: cache._FileMemo) -> str:
        return self.destinationAccount

    def file_date(self, file: cache._FileMemo) -> datetime.date:
        return datetime.date.today()

    def GetQifAccount(self) -> Optional[Account]:
        try:
            return self.qifObject.accounts[self.qifAccount] if self.qifAccount else self.qifObject.accounts[
                'Quiffen Default Account']
        except KeyError:
            print(f'Number of accounts = {len(self.qifObject.accounts)} and specified account ({self.qifAccount}) or default account not found.')
            return None

    @staticmethod
    def GetNarration(transaction: Transaction) -> Optional[str]:
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

    @staticmethod
    def GetInvertSign(accounttype: AccountType) -> Optional[bool]:
        match accounttype:
            case AccountType.CASH | AccountType.BANK:
                return False
            case AccountType.CREDIT_CARD:
                return True
            case _:
                print(f'Unknown account type: {accounttype}')
                return None
