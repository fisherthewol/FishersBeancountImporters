import unittest
import datetime

from beancount.ingest import cache
from beancount.core.amount import Amount
from beancount.core.number import D
from beancountimporters.FirstAccountImporter.FirstAccountImporter import Importer, csv_to_list
from tests.Utilities import GetTestFilesDir


class FirstAccountTestCase(unittest.TestCase):

    def setUp(self):
        self.importer = Importer(currentaccount="CurrentAccount", flag="!")
        testFilesDir = GetTestFilesDir()
        self.salaryFile = cache._FileMemo((testFilesDir / "2024-10-25 My Payslip 28-OCT-24.pdf").absolute().as_posix())
        self.amexFile = cache._FileMemo((testFilesDir / "Amex.csv").absolute().as_posix())
        self.firstDirectFile = cache._FileMemo((testFilesDir / "FirstDirect.csv").absolute().as_posix())

    def test_CSVToListImportsCorrectly(self):
        listResult = csv_to_list(self.firstDirectFile.name)
        self.assertEqual(len(listResult), 18)

    def test_ImporterCorrectlyIdentifiesFDCSV(self):
        fdIdentify = self.importer.identify(self.firstDirectFile)
        self.assertEqual(fdIdentify, True)

    def test_ImporterCorrectlyDeniesSalaryFile(self):
        fdIdentify = self.importer.identify(self.salaryFile)
        self.assertEqual(fdIdentify, False)

    def test_FileAccount(self):
        account = self.importer.file_account(self.firstDirectFile)
        self.assertEqual(account, "CurrentAccount")

    def test_FileDate(self):
        date = self.importer.file_date(self.firstDirectFile)
        self.assertEqual(date, datetime.date.today())

    def test_Extract(self):
        txns = self.importer.extract(self.firstDirectFile)
        self.assertEqual(len(txns), 18)

        testTxn = txns[7]
        self.assertEqual(testTxn.date, datetime.date(2023, 1, 10))
        self.assertEqual(testTxn.payee, None)
        self.assertEqual(testTxn.narration, "NYA*Decorum VendinAberystwyth")
        self.assertEqual(len(testTxn.postings), 1)
        self.assertEqual(testTxn.tags, frozenset())
        self.assertEqual(testTxn.links, frozenset())

        posting = testTxn.postings[0]
        self.assertEqual(posting.account, "CurrentAccount")
        self.assertEqual(posting.units, Amount(-D("2.40"), "GBP"))

if __name__ == '__main__':
    unittest.main()
