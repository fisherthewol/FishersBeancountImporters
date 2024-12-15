import datetime
import unittest
from beancountimporters.AccessSalaryImporter.AccessSalaryImporter import Importer, pdf_to_text
from beancount.ingest import cache
from beancount.core.amount import Amount
from beancount.core.number import D


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
        self.salaryFile = cache._FileMemo("./TestFiles/2024-10-25 My Payslip 28-OCT-24.pdf")
        self.amexFile = cache._FileMemo("./TestFiles/Amex.csv")
        with open("./TestFiles/SalaryText.txt", 'r', encoding="unicode_escape") as file:
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

    def test_ExtractionReturnsCorrectValues(self):
        transactions = self.importer.extract(self.salaryFile)
        self.assertEqual(len(transactions), 1)
        transaction = transactions[0]
        self.assertEqual(transaction.date, datetime.date(2024, 10, 28))
        self.assertEqual(transaction.payee, "SELF")
        self.assertEqual(len(transaction.postings), 7)
        self.assertEqual(transaction.tags, frozenset())
        self.assertEqual(transaction.links, frozenset())

        postings = transaction.postings

        netPay = postings[0]
        self.assertEqual(netPay.account, "CurrentAccount")
        self.assertEqual(netPay.units, Amount(D("2112.33"), "GBP"))

        studentLoan = postings[1]
        self.assertEqual(studentLoan.account, "StudentLoanAccount")
        self.assertEqual(studentLoan.units, Amount(D("28.00"), "GBP"))

        payTax = postings[2]
        self.assertEqual(payTax.account, "PAYE")
        self.assertEqual(payTax.units, Amount(D("328.60"), "GBP"))

        natInsurance = postings[3]
        self.assertEqual(natInsurance.account, "NationalInsuranceAccount")
        self.assertEqual(natInsurance.units, Amount(D("123.56"), "GBP"))

        pensionAsset = postings[4]
        self.assertEqual(pensionAsset.account, "PensionAssetAccount")
        self.assertEqual(pensionAsset.units, Amount(D("283.34"), "GBP"))

        pensionMatch = postings[5]
        self.assertEqual(pensionMatch.account, "PensionMatchAccount")
        self.assertEqual(pensionMatch.units, Amount(-D("141.67"), "GBP"))

        grossPay = postings[6]
        self.assertEqual(grossPay.account, "SalaryAccount")
        self.assertEqual(grossPay.units, Amount(-D("2,833.33"), "GBP"))



if __name__ == '__main__':
    unittest.main()
