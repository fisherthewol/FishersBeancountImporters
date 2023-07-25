from typing import Dict, List, Callable

from beancount.core import flags
from beancount.core.amount import Amount
from beancount.core.data import Posting
from beancount.core.number import D


class CSVHeuristics:
    def __init__(self,
                 payeecolumn: str,
                 valuecolumn: str,
                 groceriesaccount: str,
                 phoneaccount: str,
                 currency: str = "GBP",
                 invertvalue: bool = True,
                 grocerystores: List = None):
        """
        Create a class to perform heuristics.
        :param payeecolumn: Column to read Payee from.
        :param valuecolumn: Column to read Value from.
        :param groceriesaccount: Account to pay groceries into.
        :param phoneaccount: Account to pay phone bill into.
        :param currency: Currency to use.
        :param invertvalue: Whether the posting should have an inverted value.
                            Set this to the inverse of the units in the calling class.
        """
        self.payeeColumn = payeecolumn
        self.valueColumn = valuecolumn
        self.groceriesAccount = groceriesaccount
        self.phoneAccount = phoneaccount
        self.currency = currency
        self.invertValue = invertvalue
        self.groceryStores = grocerystores if grocerystores else ['tesco', 'morrison', 'lidl', 'aldi']

    def identify(self, row: Dict[str, str]) -> Posting:
        functions = [getattr(self, func) for func in dir(self) if
                     func.startswith("identify_")
                     and callable(getattr(self, func))]
        for function in functions:
            if (identified := function(row)) is not None:
                return identified

    def identify_groceries(self, row: Dict[str, str]) -> Posting:
        desc: str = row[self.payeeColumn]
        for store in self.groceryStores:
            if store in desc.lower():
                return Posting(
                    account=self.groceriesAccount,
                    units=Amount(
                        -D(row[self.valueColumn]) if self.invertValue else D(row[self.valueColumn]),
                        self.currency
                    ),
                    cost=None, price=None, flag=flags.FLAG_WARNING, meta=None
                )
        return None

    def identify_phone(self, row: Dict[str, str]) -> Posting:
        desc: str = row[self.payeeColumn]
        if 'smarty' in desc.lower():
            return Posting(
                account=self.phoneAccount,
                units=Amount(
                    -D(row[self.valueColumn]) if self.invertValue else D(row[self.valueColumn]),
                    self.currency
                ),
                cost=None, price=None, flag=flags.FLAG_WARNING, meta=None
            )
        return None
