from typing import Dict

from beancount.core.amount import Amount
from beancount.core.data import Posting
from beancount.core.number import D


class Heuristics:
    def __init__(self):
        self.groceryStores = ['tesco', 'morrison', 'lidl', 'aldi']

    def identify_groceries(self, row: Dict[str], groceriesaccount: str) -> Posting:
        desc: str = row['Description']
        for store in self.groceryStores:
            if store in desc.lower():
                return Posting(
                    account=groceriesaccount,
                    units=Amount(-D(row['Amount']), self.currency),
                    cost=None, price=None, flag=None, meta=None
                )
        return None