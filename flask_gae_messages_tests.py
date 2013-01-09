#!/usr/bin/env python
try:
  # a hack to see if the app engine sdk is loaded..
  import yaml
except ImportError:
  import dev_appserver
  dev_appserver.fix_sys_path()

import unittest
from flask.ext import gae_tests
from flask.ext import gae_messages
from google.appengine.api import taskqueue
from jinja2 import Environment
from jinja2.loaders import DictLoader

class TestCase(gae_tests.TestCase):
  def setUp(self):
    gae_tests.TestCase.setUp(self)
    self.env = Environment(loader=DictLoader({
      'subject.tpl': '{{var}}',
      'message.html.tpl': '<html>{{var}}</html>',
      'message.text.tpl': '{{var}}',
    }))

  def test_template_sanity_check(self):
    tpl = self.env.get_template("subject.tpl")
    self.assertIsNotNone(tpl)

  def test_send_enqueues_and_returns_task(self):
    message = gae_messages.Message(
      sender='test@domain.com',
      subject=self.env.get_template("subject.tpl"),
      template_html=self.env.get_template("message.html.tpl"),
      template_text=self.env.get_template("message.text.tpl"))

    task = message.send(
      to='test@gmail.com',
      method=gae_messages.Method.EMAIL,
      context={'var': 'testing'})

    self.assertIsInstance(task, taskqueue.Task)


if __name__ == '__main__':
  unittest.main()
