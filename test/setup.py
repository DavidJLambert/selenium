""" setup.py

SUMMARY: Use Selenium to watch for new online jobs on Wyzant.com.

REPOSITORY: https://github.com/DavidJLambert/Selenium

AUTHOR: David J. Lambert

VERSION: 0.1.0

DATE: Jul 3, 2020
"""
from distutils.core import setup

with open("README.rst", 'r') as f:
    long_description = f.read()

setup(
    author='David J. Lambert',
    author_email='David5Lambert7@gmail.com',
    description='Python Universal Database Client',
    license='MIT License',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    name='UniversalClient',
    py_modules=["UniversalClient"],
    url='https://github.com/DavidJLambert/Python-Universal-DB-Client',
    version='0.2.7',
    install_requires=[
        cx_Oracle,
        psutil,
        psycopg2,
        pymysql,
        pyodbc,
        pytest,
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: End Users/Desktop',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Database :: Front-Ends',
    ],
)
