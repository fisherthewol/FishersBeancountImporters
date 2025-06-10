import unittest

from beangulp import cache
from beancountimporters.ofximporter.ofxImporter import ofxImporter
from tests.Utilities import GetTestFilesDir


class ofxTestCase(unittest.TestCase):

    def setUp(self):
        self.importer = ofxImporter(destinationaccount="DestinationAccount")
        testFilesDir = GetTestFilesDir()
        self.salaryFile = cache._FileMemo((testFilesDir / "2024-10-25 My Payslip 28-OCT-24.pdf").absolute().as_posix())
        self.lloydsCcFile = cache._FileMemo((testFilesDir / "LloydsCC.qif").absolute().as_posix())
        self.natwestCcFile = cache._FileMemo((testFilesDir / "natwestcc.ofx").absolute().as_posix())

    def test_Name(self):
        self.assertEqual("ofxImporter.DestinationAccount", self.importer.name())

    def test_ImporterCorrectlyIdentifiesNatwestOFX(self):
        natwestIdentify = self.importer.identify(self.natwestCcFile)
        self.assertTrue(natwestIdentify)


if __name__ == '__main__':
    unittest.main()
