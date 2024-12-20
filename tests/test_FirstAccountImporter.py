import unittest
import datetime

from beancount.ingest import cache
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

    def test_ImporterCorrectlyIdentifiesAmexCSV(self):
        fdIdentify = self.importer.identify(self.firstDirectFile)
        self.assertEqual(fdIdentify, True)

    def test_ImporterCorrectlyDeniesSalaryFile(self):
        fdIdentify = self.importer.identify(self.salaryFile)
        self.assertEqual(fdIdentify, False)

    def test_FileAccount(self):
        account = self.importer.file_account(self.firstDirectFile)
        self.assertEqual(account, "CurrentAccount")

    def test_FileDate(self):
        date = self.importer.file_date(self.amexFile)
        self.assertEqual(date, datetime.date.today())

if __name__ == '__main__':
    unittest.main()
