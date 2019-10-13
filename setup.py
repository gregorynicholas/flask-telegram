#!/usr/bin/env python
"""
flask-telegram

flask extension for delivering messages. send via the app engine mail or xmpp
apis, and/or other third party providers such as sendgrid.


links:

* docs: http://gregorynicholas.github.io/flask-telegram
* source: http://github.com/gregorynicholas/flask-telegram
* package: http://packages.python.org/flask-telegram
* travis-ci: http://travis-ci.org/gregorynicholas/flask-telegram

"""
from setuptools import setup

__version__ = "0.0.2"


setup(
  name='flask-telegram',
  version=__version__,
  url='http://github.com/gregorynicholas/flask-telegram',
  license='MIT',
  author='gregorynicholas',
  author_email='gn@gregorynicholas.com',
  description=__doc__,
  long_description=__doc__,
  zip_safe=False,
  platforms='any',
  install_requires=[
    "flask==0.9",
    "werkzeug==0.15.3",
    "blinker==1.2",
  ],
  py_modules=[
    "flask_telegram",
    "flask_telegram_gaemail",
  ],
  tests_require=[
    "blinker==1.2",
    "flask-gae_tests==1.0.1",
  ],
  test_suite='flask_telegram_tests',
  classifiers=[
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development :: Libraries :: Python Modules'
  ]
)
