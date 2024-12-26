import unittest
import datetime

from beancount.ingest import cache
from beancount.core.amount import Amount
from beancount.core.number import D
from beancountimporters.HSBCCCImporter.HSBCCCImporter import Importer, csv_to_list
from tests.Utilities import GetTestFilesDir


class HSBCCCTestCase(unittest.TestCase):

    def setUp(self):
        self.importer = Importer(creditcardaccount="CreditCardAccount", flag="!")
        testFilesDir = GetTestFilesDir()
        self.salaryFile = cache._FileMemo((testFilesDir / "2024-10-25 My Payslip 28-OCT-24.pdf").absolute().as_posix())
        self.hsbcccFile = cache._FileMemo((testFilesDir / "HSBCCreditCard.csv").absolute().as_posix())

    def test_CSVToListImportsCorrectly(self):
        listResult = csv_to_list(self.hsbcccFile.name)
        self.assertEqual(len(listResult), 9)

    def test_ImporterCorrectlyIdentifiesHSBCCSV(self):
        hsbcIdentify = self.importer.identify(self.hsbcccFile)
        self.assertEqual(hsbcIdentify, True)

    def test_ImporterCorrectlyDeniesSalaryFile(self):
        hsbcIdentify = self.importer.identify(self.salaryFile)
        self.assertEqual(hsbcIdentify, False)

    def test_FileAccount(self):
        account = self.importer.file_account(self.hsbcccFile)
        self.assertEqual(account, "CreditCardAccount")

    def test_FileDate(self):
        date = self.importer.file_date(self.hsbcccFile)
        self.assertEqual(date, datetime.date.today())

    def test_Extract(self):
        txns = self.importer.extract(self.hsbcccFile)
        self.assertEqual(len(txns), 9)

        testTxn = txns[3]
        self.assertEqual(testTxn.date, datetime.date(2023, 3, 18))
        self.assertEqual(testTxn.payee, "WWW.CEF.CO.UK          01926865061   GB")
        self.assertEqual(testTxn.narration, "WWW.CEF.CO.UK          01926865061   GB")
        self.assertEqual(len(testTxn.postings), 1)
        self.assertEqual(testTxn.tags, frozenset())
        self.assertEqual(testTxn.links, frozenset())

        posting = testTxn.postings[0]
        self.assertEqual(posting.account, "CreditCardAccount")
        self.assertEqual(posting.units, Amount(-D("135.30"), "GBP"))

if __name__ == '__main__':
    unittest.main()
