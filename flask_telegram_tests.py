#!/usr/bin/env python
"""
  flask.ext.telegram_tests
  ~~~~~~~~~~~~~~~~~~~~~~~~

"""
from __future__ import unicode_literals

# avoid webapp25 imports from the deferred lib.. fucking gae..
import os
os.environ["APPENGINE_RUNTIME"] = "python27"
try:
  import dev_appserver
  dev_appserver.fix_sys_path()
except ImportError:
  pass

import unittest
import flask
from flask.ext import gae_tests
from flask.ext import telegram
from jinja2 import Environment
from jinja2.loaders import DictLoader


class MessageTemplate(telegram.MessageTemplateMixin):
  """
  messagetemplate class.
  """


class TestCase(gae_tests.TestCase):
  def setUp(self):
    gae_tests.TestCase.setUp(self)
    self.jinja_env = Environment(loader=DictLoader({
      'subject.html': '{{var}}',
      'body.html': '<html>{{var}}</html>',
      'body.txt': '{{var}}',
    }))

    self.flaskapp = flask.Flask(__name__)
    telegram.init_app(self.flaskapp)
    self.flaskapp._app_context = self.flaskapp.app_context()
    self.flaskapp._app_context.push()

  def tearDown(self):
    self.flaskapp._app_context.pop()
    self.flaskapp._app_context = None
    gae_tests.TestCase.tearDown(self)

  def test_template_sanity_check(self):
    tpl = self.jinja_env.get_template("subject.html")
    self.assertIsNotNone(tpl)

  def test_send_enqueues_and_returns_task(self):
    # setup the template..
    messagetemplate = MessageTemplate(
      sender="sender@domain.com",
      subject_template="subject.html",
      body_html_template="body.html",
      body_text_template="body.html",
      jinja_env=self.jinja_env)
    message = telegram.Message(messagetemplate)

    message.deliver(
      recipient='test@gmail.com',
      var="testing")

    self.assertTasksInQueue(1)


if __name__ == '__main__':
  unittest.main()
