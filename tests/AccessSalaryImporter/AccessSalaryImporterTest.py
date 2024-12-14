import datetime
import unittest
from beancountimporters.AccessSalaryImporter.AccessSalaryImporter import Importer, pdf_to_text
from beancount.ingest import cache


class AccessSalaryTestCase(unittest.TestCase):

    def setUp(self):
        self.importer = Importer(
            salaryaccount="SalaryAccount",
            currentaccount="CurrentAccount",
            paye="PAYE",
            pensionmatchaccount="PensionMatchAccount",
            nationalinsuranceaccount="NationalInsuranceAccount",
            pensionassetaccount="PensionAssetAccount",
            studentloanaccount="StudentLoanAccount",
            y2kfix="20",
            flag="!")
        self.salaryFile = cache._FileMemo("../TestFiles/2024-10-25 My Payslip 28-OCT-24.pdf")
        self.amexFile = cache._FileMemo("../TestFiles/Amex.csv")
        with open("../TestFiles/SalaryText.txt", 'r', encoding="unicode_escape") as file:
            self.salaryText = file.read()

    def test_pdfToTextCorrectlyExtracts(self):
        pdfText = pdf_to_text(self.salaryFile.name)
        self.assertEqual(pdfText, self.salaryText)

    def test_ImporterCorrectlyIdentifiesPaychequePDF(self):
        salaryIndentify = self.importer.identify(self.salaryFile)
        self.assertEqual(salaryIndentify, True)

    def test_ImporterCorrectlyDeniesAmexCSV(self):
        salaryIndentify = self.importer.identify(self.amexFile)
        self.assertEqual(salaryIndentify, False)

    def test_FileAccount(self):
        account = self.importer.file_account(self.salaryFile)
        self.assertEqual(account, "SalaryAccount")

    def test_FileDate(self):
        date = self.importer.file_date(self.salaryFile)
        self.assertEqual(date, datetime.date(2024, 10, 28))


if __name__ == '__main__':
    unittest.main()
