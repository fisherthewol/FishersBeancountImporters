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
        with open("../TestFiles/SalaryText.txt", 'r', encoding="unicode_escape") as file:
            self.salaryText = file.read()

    def test_ImporterCorrectlyIdentifiesPaychequePDF(self):
        salaryIndentify = self.importer.identify(self.salaryFile)
        self.assertEqual(salaryIndentify, True)

    def test_pdfToTextCorrectlyExtracts (self):
        pdfText = pdf_to_text(self.salaryFile.name)
        self.assertEqual(pdfText, self.salaryText)


if __name__ == '__main__':
    unittest.main()
