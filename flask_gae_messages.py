"""
  flask_gae_messages
  ~~~~~~~~~~~~~~~~~~~

  Flask extension for working with messages using the mail &
  xmpp api's on App Engine.

  :copyright: (c) 2012 by gregorynicholas.
  :license: MIT, see LICENSE for more details.

  :usage:
    from flask.ext import gae_messages
    from jinja2 import Environment
    from jinja2.loaders import DictLoader
    env = Environment(loader=DictLoader({
      'subject.tpl': '{{var}}',
      'message.html.tpl': '<html>{{var}}</html>',
      'message.text.tpl': '{{var}}',
    }))

    message = gae_messages.Message(
      sender='test@domain.com',
      subject=env.get_template("subject.tpl"),
      template_html=env.get_template("message.html.tpl"),
      template_text=env.get_template("message.text.tpl"))

    message.send(
      to='test@gmail.com',
      method=Method.EMAIL,
      context={'var': 'testing'})
"""
try:
  # a hack to see if the app engine sdk is loaded..
  import yaml
except ImportError:
  import dev_appserver
  dev_appserver.fix_sys_path()
import blinker
import logging
from jinja2 import Template
from google.appengine.ext import ndb
from google.appengine.api import mail
# from google.appengine.api import xmpp
from google.appengine.ext import deferred

__all__ = ['QUEUE_NAME', 'MessageTemplate', 'Method', 'Message', 'queue']

QUEUE_NAME = 'default'

class MessageTemplate(ndb.Model):
  '''Data model for storing templates in the datastore.

    :param sender: Email address of the sender.
    :param subject: String.
    :param template_html: String.
    :param template_text: String.
  '''
  sender = ndb.StringProperty(indexed=False)
  subject = ndb.StringProperty(indexed=False)
  template_html = ndb.TextProperty(indexed=False)
  template_text = ndb.TextProperty(indexed=False)

class Method:
  '''Enum for the different methods to send a message.'''
  #:
  SMS = 1
  #:
  XMPP = 2
  #:
  EMAIL = 3
  #:
  FLASH = 4

class Message:
  '''
    :param sender: String, email address of the sender.
    :param subject: instance of ```jinja2.Template```.
    :param template_html: instance of ```jinja2.Template```.
    :param template_text: instance of ```jinja2.Template```.
    :param in_reply_to:
  '''
  def __init__(self, sender, subject=None, template_html=None,
    template_text=None, in_reply_to=None):
    if isinstance(template_text, Template) and \
       not isinstance(template_text, Template):
      raise ValueError(
        'message must have a template an instance of ```jinja2.Template```')
    self.sender = sender
    self.subject = subject
    self.in_reply_to = in_reply_to
    self.template_text = template_text
    self.template_html = template_html

  def render_subject(self, context):
    return self.subject.render(**context).encode('utf-8')

  def render_body_text(self, context):
    return self.template_text.render(**context).encode('utf-8')

  def render_body_html(self, context):
    return self.template_html.render(**context).encode('utf-8')

  def send(self, to, context, method=Method.EMAIL, background=True):
    '''Send a message to a designated `to` recipient.

      :param to: String, email address of the recipient.
      :param context:
          a ```dict``` of replacements to set for the message being sent, if
          one or more required paramaters for the template specified is missing
          a ```ValueError``` will be raised.
      :param method: Enum of the method to send a message.
      :param background: Send through a background taskqueue.

      :returns:
          an instance of a ```taskqueue.Task``` object.
    '''
    if context and not isinstance(context, dict):
      raise ValueError('`context` must be a `dict`.')
    _execute = None
    if background:
      _execute = queue
    else:
      _execute = _notification_meth_to_send_mapping[method]
    return _execute(
      to=to,
      sender=self.sender,
      subject=self.render_subject(context),
      body_text=self.render_body_text(context),
      body_html=self.render_body_html(context),
      method=method)


def queue(to, sender, subject, body_text, body_html, method=Method.EMAIL):
  '''Enqueue a background task to send a message.

    :param to: String, address of the recipient.
    :param sender: String, address of the sender.
    :param subject: String, subject of the message.
    :param body_text: String, plain text body of the message.
    :param body_html: String, HTML body of the message.
    :param method: Enum of the method to send a message.
  '''
  return deferred.defer(_notification_meth_to_send_mapping[method],
    to, sender, subject, body_text, body_html, _queue=QUEUE_NAME)

def send_mail(to, sender, subject, body_text, body_html):
  '''Send a message as an email.'''
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
    import traceback as tb
    logging.exception(
      'Exception sending notification email: %s' % tb.format_ext())

def send_sms(to, sender, subject, body_text, body_html):
  '''Send a message as a sms.'''
  raise NotImplemented()

def send_xmpp(to, sender, subject, body_text, body_html):
  '''Send a message as a xmpp.'''
  raise NotImplemented()

def send_flash(to, sender, subject, body_text, body_html):
  raise NotImplemented()

_notification_meth_to_send_mapping = {
  Method.SMS: send_sms,
  Method.XMPP: send_xmpp,
  Method.EMAIL: send_mail,
  Method.FLASH: send_flash,
}

# setup signals..

signals = blinker.Namespace()
email_dispatched = signals.signal("email-dispatched", doc="""
Signal sent when an email is dispatched. This signal will also be sent
in testing mode, even though the email will not actually be sent.
""")