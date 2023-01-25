def main():
    import AccessSalaryImporter
    from beancount.ingest import cache
    import os

    # fc = cache.get_file(os.getcwd() + "/AccessSalaryImporter/My Payslip 22-DEC-22.pdf")
    # imp = AccessSalaryImporter.Importer("", "", "20")
    # print(imp.identify(fc))
    # x = imp.extract(fc)
    # print(x)
    import FirstAccountImporter
    from beancount.ingest import cache
    fc = cache.get_file(os.getcwd() + "/FirstAccountImporter/25012023_1621.csv")
    imp = FirstAccountImporter.Importer("")
    x = imp.identify(fc)
    print(x)
    y = imp.extract(fc)


if __name__ == '__main__':
    main()
