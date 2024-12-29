import decimal
import unittest
import datetime

from beancount.ingest import cache
from beancount.core.amount import Amount
from beancount.core.number import D
from beancountimporters.QifImporter.QifImporter import QifImporter
from tests.Utilities import GetTestFilesDir

from quiffen import Qif, Category, Transaction, AccountType


class QifTestCase(unittest.TestCase):

    def setUp(self):
        self.importer = QifImporter(destinationaccount="DestinationAccount", dayfirst=True)
        testFilesDir = GetTestFilesDir()
        self.salaryFile = cache._FileMemo((testFilesDir / "2024-10-25 My Payslip 28-OCT-24.pdf").absolute().as_posix())
        self.lloydsCcFile = cache._FileMemo((testFilesDir / "LloydsCC.qif").absolute().as_posix())
        self.dummyQifObject = Qif.parse(self.lloydsCcFile.name, day_first=True)

    def test_Name(self):
        self.assertEqual(self.importer.name(), "QifImporter.DestinationAccount")

    def test_ImporterCorrectlyIdentifiesLloydsQIF(self):
        lloydsIdentify = self.importer.identify(self.lloydsCcFile)
        self.assertEqual(lloydsIdentify, True)

    def test_ImporterCorrectlyDeniesSalaryFile(self):
        lloydsIdentify = self.importer.identify(self.salaryFile)
        self.assertEqual(lloydsIdentify, False)

    def test_FileAccount(self):
        account = self.importer.file_account(self.lloydsCcFile)
        self.assertEqual(account, "DestinationAccount")

    def test_FileDate(self):
        date = self.importer.file_date(self.lloydsCcFile)
        self.assertEqual(date, datetime.date.today())

    def test_Extract(self):
        txns = self.importer.extract(self.lloydsCcFile)
        self.assertEqual(len(txns), 12)

        testTxn = txns[3]
        self.assertEqual(testTxn.date, datetime.date(2024, 12, 20))
        self.assertEqual(testTxn.payee, "Goosedale")
        self.assertEqual(testTxn.narration, None)
        self.assertEqual(len(testTxn.postings), 1)
        self.assertEqual(testTxn.tags, frozenset())
        self.assertEqual(testTxn.links, frozenset())

        posting = testTxn.postings[0]
        self.assertEqual(posting.account, "DestinationAccount")
        self.assertEqual(posting.units, Amount(-D("4.70"), "GBP"))

    def test_GetQifAccountThrowsErrorWhenQifObjectDoesntYetExist(self):
        with self.assertRaises(ValueError) as cm:
            self.importer.GetQifAccount()

        exception = cm.exception
        self.assertEqual(str(exception), "QifObject is None so an account cannot be determined.")

    def test_GetQifDAccountReturnsDefaultAccount(self):
        self.importer.qifObject = self.dummyQifObject
        qifAccount = self.importer.GetQifAccount()
        self.assertEqual(qifAccount.name, "Quiffen Default Account")
        self.importer.qifObject = None
        self.importer.qifAccount = ""

    def test_GetQifAccountReturnsNoneForBadAccount(self):
        self.importer.qifObject = self.dummyQifObject
        self.importer.qifAccount = "BadAccount"
        qifAccount = self.importer.GetQifAccount()
        self.assertEqual(qifAccount, None)
        self.importer.qifObject = None
        self.importer.qifAccount = ""

    def test_GetNarration(self):
        tran = Transaction(
            date=datetime.datetime.now(),
            amount=decimal.Decimal(100),
        )
        # Assert an empty transaction returns None.
        narrationNoInfo = QifImporter.GetNarration(transaction=tran)
        self.assertEqual(narrationNoInfo, None)

        # Category returns category.
        cat = Category(name="TestCategory")
        tran.category = cat
        narrationCatOnly = QifImporter.GetNarration(transaction=tran)
        self.assertEqual(narrationCatOnly, f"Category: {str(cat)}")
        tran.category = None

        # Memo returns Memo.
        tran.memo = "TestMemo"
        narrationMemoOnly = QifImporter.GetNarration(transaction=tran)
        self.assertEqual(narrationMemoOnly, "Memo: TestMemo")
        tran.memo = None

        # Cleared returns formatted date.
        tran.cleared = str(datetime.datetime(2024, 12, 29, 12, 00, 00, 00))
        narrationClearedOnly = QifImporter.GetNarration(transaction=tran)
        self.assertEqual(narrationClearedOnly, f"Cleared: {str(datetime.datetime(2024, 12, 29, 12, 00, 00, 00))}")
        tran.cleared = None

        # CheckNumber returns CheckNumber
        tran.check_number = 12456
        narrationCheckOnly = QifImporter.GetNarration(transaction=tran)
        self.assertEqual(narrationCheckOnly, "Check Number: 12456")
        tran.check_number = None

        # All returns a comma list:
        tran.category = cat
        tran.memo = "TestMemo"
        tran.cleared = str(datetime.datetime(2024, 12, 29, 12, 00, 00, 00))
        tran.check_number = 12456
        narrationAll = QifImporter.GetNarration(transaction=tran)
        self.assertEqual(narrationAll,
                         f"Memo: TestMemo, Cleared: {str(datetime.datetime(2024, 12, 29, 12, 00, 00, 00))}, Category: {str(cat)}, Check Number: 12456")

    def test_GetInvertSign(self):
        # Assert currently unhandled account types return None
        acc = AccountType("Oth A")
        actual = QifImporter.GetInvertSign(acc)
        self.assertEqual(actual, None)
        acc = AccountType("Oth L")
        actual = QifImporter.GetInvertSign(acc)
        self.assertEqual(actual, None)
        acc = AccountType("Invoice")
        actual = QifImporter.GetInvertSign(acc)
        self.assertEqual(actual, None)
        acc = AccountType("Invst")
        actual = QifImporter.GetInvertSign(acc)
        self.assertEqual(actual, None)
        acc = AccountType("Unknown")
        actual = QifImporter.GetInvertSign(acc)
        self.assertEqual(actual, None)

        """
        So I'm currently assuming, based on how Lloyds produces QIF, that
        * Transactions are always from the perspective of growing a balance
        * Ergo for Asset Accounts, If the transaction is a positive, then it is a payment in, which increases its balance.
        * And for Liability Accounts, If the transaction is a positive, then it is a payment out, which increases the balance /owed/.
        Which is represented as a negative on the liability account, so we need to decrease the balance, inverting the sign.
        """
        # Assert that "Asset" accounts return false
        acc = AccountType("Cash")
        actual = QifImporter.GetInvertSign(acc)
        self.assertEqual(actual, False)
        acc = AccountType("Bank")
        actual = QifImporter.GetInvertSign(acc)
        self.assertEqual(actual, False)

        # And that "Liability" accounts return True.
        acc = AccountType("CCard")
        actual = QifImporter.GetInvertSign(acc)
        self.assertEqual(actual, True)


if __name__ == '__main__':
    unittest.main()
