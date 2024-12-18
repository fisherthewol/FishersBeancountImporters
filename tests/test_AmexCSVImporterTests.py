import unittest
import datetime
import unittest
from beancountimporters.AmexCSVImporter.AmexCSVImporter import Importer, csv_to_list
from beancount.ingest import cache
from beancount.core.amount import Amount
from beancount.core.number import D

class AmexCSVTestCase(unittest.TestCase):

    def setUp(self):
        self.importer = Importer(creditcardaccount="CreditCardAccount", flag="!")
        self.salaryFile = cache._FileMemo("./tests/TestFiles/2024-10-25 My Payslip 28-OCT-24.pdf")
        self.amexFile = cache._FileMemo("./tests/TestFiles/Amex.csv")

    def test_CSVToListImportsCorrectly(self):
        listResult = csv_to_list(self.amexFile.name)
        self.assertEqual(len(listResult), 14)

    def test_ImporterCorrectlyIdentifiesAmexCSV(self):
        amexIdentify = self.importer.identify(self.amexFile)
        self.assertEqual(amexIdentify, True)

    def test_ImporterCorrectlyDeniesSalaryFile(self):
        amexIdentify = self.importer.identify(self.salaryFile)
        self.assertEqual(amexIdentify, False)

    def test_FileAccount(self):
        account = self.importer.file_account(self.amexFile)
        self.assertEqual(account, "CreditCardAccount")

    def test_FileDate(self):
        date = self.importer.file_date(self.amexFile)
        self.assertEqual(date, datetime.date.today())

    def test_Extract(self):
        txns = self.importer.extract(self.amexFile)
        self.assertEqual(len(txns), 8)

        testTxn = txns[3]
        self.assertEqual(testTxn.date, datetime.date(2024, 10, 18))
        self.assertEqual(testTxn.payee, None)
        self.assertEqual(testTxn.narration, "GEORGE MICHNIEWICZ - MC HULL")
        self.assertEqual(len(testTxn.postings), 1)
        self.assertEqual(testTxn.meta["reference"], "'AT242930041000011728613'")
        self.assertEqual(testTxn.tags, frozenset())
        self.assertEqual(testTxn.links, frozenset())

        posting = testTxn.postings[0]
        self.assertEqual(posting.account, "CreditCardAccount")
        self.assertEqual(posting.units, Amount(-D("2.19"), "GBP"))


if __name__ == '__main__':
    unittest.main()
