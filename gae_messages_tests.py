#!/usr/bin/env python
try:
  # a hack to see if the app engine sdk is loaded..
  import yaml
except ImportError:
  import dev_appserver
  dev_appserver.fix_sys_path()

import unittest
import gae_upload
from flask import json
from flask import Flask, Request
from flask.testsuite import FlaskTestCase
from google.appengine.api import files
from google.appengine.ext import testbed
from StringIO import StringIO

class FileObj(StringIO):
  def close(self):
    print 'in file close..'

class _Request(Request):
  def _get_file_stream(*args, **kwargs):
    return FileObj()

# test application..
app = Flask(__name__)
app.debug = True
app.request_class = _Request


@app.route('/test_upload1', methods=['POST', 'OPTIONS', 'HEAD', 'PUT'])
@gae_upload.upload_blobs()
def test_upload1(blobs):
  return json.dumps(blobs.to_dict())

class TestCase(FlaskTestCase):

  def setUp(self):
    FlaskTestCase.setUp(self)
    # First, create an instance of the Testbed class.
    self.testbed = testbed.Testbed()
    # Then activate the testbed, which prepares the
    # service stubs for use
    self.testbed.activate()
    # Next, declare which service stubs you want to use.
    self.testbed.init_mail_stub()
    self.testbed.init_memcache_stub()
    self.testbed.init_blobstore_stub()
    self.testbed.init_taskqueue_stub()
    self.testbed.init_datastore_v3_stub()

  def test_blobstore_sanity_check(self):
    filename = files.blobstore.create(mime_type='application/octet-stream')
    self.assertNotEquals(None, filename)
    with files.open(filename, 'a') as f:
      f.write('blobdata')
    files.finalize(filename)
    blobkey = files.blobstore.get_blob_key(filename)
    self.assertNotEquals(None, blobkey)

  def test_upload_returns_valid_blob_result(self):
    filename = 'test_file.jpg'
    f = open(filename, 'r')
    data = f.read()
    size = len(data)
    f.close()
    response = app.test_client().post(
      data={'test': (StringIO(data), 'test_file.jpg')},
      path='/test_upload1',
      headers={},
      query_string={})
    self.assertEqual(200, response.status_code)
    result = json.loads(response.data)
    self.assertIsInstance(result, list)
    self.assertEquals(1, len(result))
    self.assertEquals(True, result[0].get('successful'))
    # check the file name is the same..
    self.assertEquals(filename, result[0].get('name'))
    # check file size is the same..
    self.assertEquals(size, result[0].get('size'))
    # validate the blob_key..
    self.assertTrue(len(result[0].get('blob_key')) > 0)

if __name__ == '__main__':
  unittest.main()
