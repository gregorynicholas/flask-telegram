"""
  gae_messages
  ~~~~~~~~~~~~~~~~~~~

  Flask extension for working with messages using the mail &
  xmpp api's on App Engine.

  :copyright: (c) 2012 by gregorynicholas.
  :license: MIT, see LICENSE for more details.

  :usage:
    from jinja2 import Environment
    from jinja2.loaders import DictLoader
    env = Environment(loader=DictLoader({
      'subject.tpl': '{{var}}',
      'message.html.tpl': '<html>{{var}}</html>',
      'message.text.tpl': '{{var}}',
    }))
    tpl = env.get_template("tpl.html")
    message = gae_messages.Message(
      sender='test@domain.com',
      subject=env.get_template("subject.tpl"),
      template_html=env.get_template("message.html.tpl"),
      template_text=env.get_template("message.text.tpl"))
    messages.send(
      to='test@gmail.com',
      replacements={'var': 'testing'},
      method=Method.EMAIL)
"""
import logging
from jinja2 import Template
from google.appengine.ext import ndb
from google.appengine.api import mail
# from google.appengine.api import xmpp
from google.appengine.ext import deferred

__all__ = ['QUEUE_NAME', 'MessageTemplate', 'Method', 'Message', 'queue']

QUEUE_NAME = 'default'

class MessageTemplate(ndb.Model):
  '''Data model for storing templates in the datastore.'''
  subject = ndb.StringProperty(indexed=False)
  sender = ndb.StringProperty(indexed=False)
  template_text = ndb.TextProperty(indexed=False)
  template_html = ndb.TextProperty(indexed=False)

class Method:
  SMS = 1
  XMPP = 2
  EMAIL = 3
  FLASH = 4

class Message:
  def __init__(self, sender, subject=None, template_html=None,
    template_text=None, in_reply_to=None):
    '''
      :param sender:
      :param subject: instance of `jinja2.Template`.
      :param template_html: instance of `jinja2.Template`.
      :param template_text: instance of `jinja2.Template`.
      :param in_reply_to:
    '''
    if isinstance(template_text, Template) and \
       not isinstance(template_html, Template):
      raise ValueError(
        'message must have a template an instance of `jinja2.Template`')
    self.sender = sender
    self.subject = subject
    self.in_reply_to = in_reply_to
    self.template_text = template_text
    self.template_html = template_html

  def render_subject(self, replacements):
    return self.subject.render(**replacements).encode('utf-8')

  def render_body_text(self, replacements):
    return self.template_text.render(**replacements).encode('utf-8')

  def render_body_html(self, replacements):
    return self.template_html.render(**replacements).encode('utf-8')

  def send(self, to, replacements, method=Method.EMAIL):
    '''
    :param to: String, email address of the recipient.
    :param replacements: a dict of paramaters to set for the message being sent,
        if one or more required paramaters for the template specified is
        missing a Value Exception will be raised.
    :param method:
  '''
    if replacements and not isinstance(replacements, dict):
      raise ValueError('`replacements` must be a `dict`.')
    return queue(
      to=to,
      sender=self.sender,
      subject=self.render_subject(replacements),
      body_text=self.render_body_text(replacements),
      body_html=self.render_body_html(replacements),
      method=method)


def queue(to, sender, subject, body_text, body_html, method=Method.EMAIL):
  '''
    :param to: String, address of the recipient.
    :param sender: String, address of the sender.
    :param subject: String, subject of the message.
    :param body_text: String, plain text body of the message.
    :param body_html: String, HTML body of the message.
  '''
  return deferred.defer(_notification_meth_to_send_mapping[method],
    to, sender, subject, body_text, body_html, _queue=QUEUE_NAME)

def _send_email(to, sender, subject, body_text, body_html):
  if to is None:
    raise ValueError('`to` is required.')
  try:
    result = mail.EmailMessage(
      to=to,
      sender=sender,
      subject=subject,
      body=body_text,
      html=body_html)
      #headers = {
      #  "In-Reply-To": email_thread_id,
      #  "References": email_thread_id,
      #},
    result.check_initialized()
    result.send()
    return result
  except:
    import traceback
    logging.exception(
      'Exception sending notification email: %s' % traceback.format_ext())

def _send_sms(to, sender, subject, body_text, body_html):
    raise NotImplemented()

def _send_xmpp(to, sender, subject, body_text, body_html):
    raise NotImplemented()

def _send_flash(to, sender, subject, body_text, body_html):
    raise NotImplemented()

_notification_meth_to_send_mapping = {
  Method.SMS: _send_sms,
  Method.XMPP: _send_xmpp,
  Method.EMAIL: _send_email,
  Method.FLASH: _send_flash,
}
