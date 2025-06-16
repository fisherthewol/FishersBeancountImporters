import datetime
import unittest
from decimal import Decimal

from beancount.core.amount import Amount
from beancount.core.number import D
from beangulp import cache

from beancountimporters.OfxImporter.OfxImporter import Importer
from tests.Utilities import GetTestFilesDir


class ofxTestCase(unittest.TestCase):

    def setUp(self):
        self.importer = Importer(destinationaccount="DestinationAccount")
        testFilesDir = GetTestFilesDir()
        self.lloydsCcFile = (testFilesDir / "LloydsCC.qif").absolute().as_posix()
        self.natwestCcFile = (testFilesDir / "natwestcc.ofx").absolute().as_posix()

    def test_Name(self):
        self.assertEqual("ofxImporter.DestinationAccount", self.importer.name)

    def test_ImporterCorrectlyIdentifiesNatwestOFX(self):
        natwestIdentify = self.importer.identify(self.natwestCcFile)
        self.assertTrue(natwestIdentify)

    def test_ImporterCorrectlyDeniesLloydsCC(self):
        lloydsIdentify = self.importer.identify(self.lloydsCcFile)
        self.assertFalse(lloydsIdentify)

    def test_FileAccount(self):
        account = self.importer.account(self.natwestCcFile)
        self.assertEqual("DestinationAccount", account)

    def test_FileDate(self):
        date = self.importer.date(self.natwestCcFile)
        self.assertEqual(datetime.date.today(), date)

    def test_Extract(self):
        txns = self.importer.extract(self.natwestCcFile, [])
        self.assertEqual(27, len(txns))

        testTxn = txns[2]
        self.assertEqual(datetime.date(2025, 5, 14), testTxn.date)
        self.assertEqual("DB FERNVERKEHR AG", testTxn.payee)
        self.assertEqual("FRANKFURT  20.40 EUR", testTxn.narration)
        self.assertEqual(2, len(testTxn.postings))
        self.assertEqual(frozenset(), testTxn.tags)
        self.assertEqual(frozenset(), testTxn.links)

        eurPosting = testTxn.postings[0]
        self.assertEqual("REPLACEME", eurPosting.account)
        self.assertEqual(Amount(D("20.40"), "EUR"), eurPosting.units)
        self.assertEqual(Amount(D("1.1819"), "GBP"), eurPosting.price)

        gbpPosting = testTxn.postings[1]
        self.assertEqual("DestinationAccount", gbpPosting.account)
        self.assertEqual(Amount(D("-17.26"), "GBP"), gbpPosting.units)

    def test_PossibleEURPosting(self):
        transaction = type('',(object,),{"memo": "TEST 20.00 EUR", "trnamt": Decimal("-15.00")})()
        posting = self.importer.PossibleEURPosting(transaction)

        self.assertEqual("REPLACEME", posting.account)
        self.assertEqual(Amount(D("20.00"), "EUR"), posting.units)
        self.assertEqual(Amount(D("0.75"), "GBP"), posting.price)


if __name__ == '__main__':
    unittest.main()
