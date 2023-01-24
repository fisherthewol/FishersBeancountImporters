from setuptools import setup, find_packages

setup(
    name="FishersBeanCountImporters",
    version="0.0.1",
    author="fisherthewol",
    packages=find_packages(['AccessSalaryImporter']),
    install_requires=[
        'PyPDF2>=3.0.1',
        'beancount @ git+https://github.com/beancount/beancount.git@6d64d56b2e04dd164cd117c124d703da89783ee1',
    ]
)
