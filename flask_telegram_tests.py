#!/usr/bin/env python
"""
  flask.ext.telegram_tests
  ~~~~~~~~~~~~~~~~~~~~~~~~

"""
try:
  # a hack to see if the app engine sdk is loaded..
  import yaml
except ImportError:
  import dev_appserver
  dev_appserver.fix_sys_path()

import unittest
from flask.ext import gae_tests
from flask.ext import telegram
from jinja2 import Environment
from jinja2.loaders import DictLoader


class MessageTemplate(telegram.MessageTemplateMixin):
  """
  data model for storing templates in the datastore.
  """
  def __init__(self, *args, **kwargs):
    telegram.MessageTemplateMixin.__init__(self, *args, **kwargs)
    super(MessageTemplate, self).__init__(*args, **kwargs)


class TestCase(gae_tests.TestCase):
  def setUp(self):
    gae_tests.TestCase.setUp(self)
    self.jinja_env = Environment(loader=DictLoader({
      'subject.html': '{{var}}',
      'body.html': '<html>{{var}}</html>',
      'body.txt': '{{var}}',
    }))

  def test_template_sanity_check(self):
    tpl = self.jinja_env.get_template("subject.html")
    self.assertIsNotNone(tpl)

  def test_send_enqueues_and_returns_task(self):
    # setup the template..
    messagetemplate = MessageTemplate(
      sender="sender@domain.com",
      subject="subject.html",
      body_html="body.html",
      body_text="body.html",
      jinja_env=self.jinja_env)
    message = telegram.Message(messagetemplate)

    message.deliver(
      receiver='test@gmail.com',
      method=telegram.DeliveryMethod.GAEMAIL,
      var="testing")

    self.assertTasksInQueue(1)


if __name__ == '__main__':
  unittest.main()
