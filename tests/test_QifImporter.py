import unittest
import datetime

from beancount.ingest import cache
from beancount.core.amount import Amount
from beancount.core.number import D
from beancountimporters.QifImporter.QifImporter import QifImporter
from tests.Utilities import GetTestFilesDir

from quiffen import Qif


class QifTestCase(unittest.TestCase):

    def setUp(self):
        self.importer = QifImporter(destinationaccount="DestinationAccount", dayfirst=True)
        testFilesDir = GetTestFilesDir()
        self.salaryFile = cache._FileMemo((testFilesDir / "2024-10-25 My Payslip 28-OCT-24.pdf").absolute().as_posix())
        self.lloydsCcFile = cache._FileMemo((testFilesDir / "LloydsCC.qif").absolute().as_posix())

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
        self.importer.qifObject = Qif.parse(self.lloydsCcFile.name, day_first=True)
        qifAccount = self.importer.GetQifAccount()
        self.assertEqual(qifAccount.name, "Quiffen Default Account")
        self.importer.qifObject = None
        self.importer.qifAccount = ""

    def test_GetQifAccountReturnsNoneForBadAccount(self):
        self.importer.qifObject = Qif.parse(self.lloydsCcFile.name, day_first=True)
        self.importer.qifAccount = "BadAccount"
        qifAccount = self.importer.GetQifAccount()
        self.assertEqual(qifAccount, None)
        self.importer.qifObject = None
        self.importer.qifAccount = ""


if __name__ == '__main__':
    unittest.main()
