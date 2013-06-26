#!/usr/bin/env python
"""
flask-telegram
~~~~~~~~~~~~~~

flask extension for delivering messages. send via the app engine mail or xmpp
apis, and/or other third party providers such as sendgrid.

links
`````

* `documentation <http://gregorynicholas.github.io/flask-telegram>`_
* `package <http://packages.python.org/flask-telegram>`_
* `source <http://github.com/gregorynicholas/flask-telegram>`_
* `development version
  <http://github.com/gregorynicholas/flask-telegram>`_

"""
from setuptools import setup

requires = open("requirements.txt", "r").readlines()

setup(
  name='flask-telegram',
  version='0.0.1',
  url='http://github.com/gregorynicholas/flask-telegram',
  license='MIT',
  author='gregorynicholas',
  author_email='gn@gregorynicholas.com',
  description='flask extension for delivering messages, send via the app '
  'engine mail or xmpp apis, and/or other third party providers such as '
  'sendgrid.',
  long_description=__doc__,
  py_modules=['flask_telegram'],
  zip_safe=False,
  platforms='any',
  install_requires=requires,
  tests_require=[
    'blinker==1.2',
    'flask_gae_tests==1.0.1',
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
