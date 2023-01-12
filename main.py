def main():
    from AccessSalaryImporter.AccessSalaryImporter import Importer
    from beancount.ingest import cache
    import os

    fc = cache.get_file(os.getcwd() + "/AccessSalaryImporter/My Payslip 22-DEC-22.pdf")
    imp = Importer("", "", "20")
    print(imp.identify(fc))
    x = imp.extract(fc)
    print(x)


if __name__ == '__main__':
    main()
