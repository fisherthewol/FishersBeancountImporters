from setuptools import setup, find_packages

setup(
    name="FishersBeanCountImporters",
    version="0.0.1",
    author="fisherthewol",
    packages=find_packages(['AccessSalaryImporter']),
    install_requires=[
        'pypdf>=3.17.0',
        'beancount==2.3.6',
    ]
)
