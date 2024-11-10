from setuptools import setup, find_packages

setup(
    name="FishersBeanCountImporters",
    version="0.0.2",
    author="fisherthewol",
    packages=find_packages(['AccessSalaryImporter']),
    install_requires=[
        'beancount==2.3.6',
        'pypdf==5.1.0',
        'quiffen==2.0.12'
    ]
)
