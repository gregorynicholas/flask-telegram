"""
Flask App Engine Notify
-----------------------

Flask extension module for working with notifications using the mail &
xmpp api's on App Engine.

Links
`````

* `documentation <http://packages.python.org/Flask%20App%20Engine%20Upload>`_
* `development version
  <http://github.com/gregorynicholas/flask-gae_notify/zipball/master#egg=Flask%20App%20Engine%20Upload-dev>`_

"""
from setuptools import setup


setup(
  name='Flask App Engine Notify',
  version='1.0.0',
  url='http://github.com/gregorynicholas/flask-gae_notify',
  license='BSD',
  author='gregorynicholas',
  description='Flask extension module for working with notifications using the \
mail & xmpp apis on App Engine.',
  long_description=__doc__,
  py_modules=['gae_notify'],
  # packages=['flaskext'],
  # namespace_packages=['flaskext'],
  include_package_data=True,
  data_files=[],
  zip_safe=False,
  platforms='any',
  install_requires=[
    'Flask'
  ],
  test_suite='gae_notify_tests',
  classifiers=[
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development :: Libraries :: Python Modules'
  ]
)
