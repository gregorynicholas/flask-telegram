"""
  flask.ext.telegram
  ~~~~~~~~~~~~~~~~~~

  flask extension for delivering messages. send via the app engine mail or xmpp
  apis, and/or other third party providers such as sendgrid.

  http://gregorynicholas.github.io/flask-telegram


  :copyright: (c) by gregorynicholas.
  :license: MIT, see LICENSE for more details.
"""
try:
  # a shitty hack to see if the app engine sdk is loaded..
  import yaml
except ImportError:
  import dev_appserver
  dev_appserver.fix_sys_path()

_signals = False
try:
  import blinker
  _signals = True
except ImportError:
  _signals = False

import logging
from jinja2 import Template
from google.appengine.api import mail
from google.appengine.ext import deferred
# from google.appengine.api import xmpp


__all__ = [
  "MessageTemplateMixin", "Message", "DeliveryMethod",
]


#:
TASKQUEUE_NAME = "default"


class MissingBodyTemplateError(ValueError):
  """
  """


class MessageTemplateMixin(object):
  """
  mixin class for the data model representing message templates.

    :param sender: string address of the sender
    :param subject: string contents of a `jinja2.Template`
    :param body_html: string contents of a `jinja2.Template`
    :param body_text: string contents of a `jinja2.Template`
    :param jinja_env: instance of `jinja2.Environment`
  """

  def __init__(
    self, sender, subject, body_html, body_text,
    jinja_env=None, *args, **kwargs):
    """
      :param sender: string address of the sender
      :param subject: string contents of a `jinja2.Template`
      :param body_html: string contents of a `jinja2.Template`
      :param body_text: string contents of a `jinja2.Template`
      :param jinja_env: instance of `jinja2.Environment`
    """
    self.jinja_env = jinja_env
    self._sender = sender
    self._subject_template = self.jinja_env.get_template(subject)
    self._body_html_template = self.jinja_env.get_template(body_html)
    self._body_text_template = self.jinja_env.get_template(body_text)

    if not (
      isinstance(self._body_html_template, Template) or
      isinstance(self._body_text_template, Template)):
      raise MissingBodyTemplateError(
        "MessageTemplate must have either html or text body template.")

  @property
  def sender(self):
    """
      :returns: string address of the sender
    """
    return self._sender

  @property
  def subject_template(self):
    """
      :returns: instance of `jinja2.Template`
    """
    return self._subject_template

  @property
  def body_html_template(self):
    """
      :returns: instance of `jinja2.Template`
    """
    return self._body_html_template

  @property
  def body_text_template(self):
    """
      :returns: instance of `jinja2.Template`
    """
    return self._body_text_template

  def _render(self, template, ctx):
    """
    calls the render method on a jinja2 template, and returns the result.

      :param template: instance of `jinja2.Template`
      :param **ctx: dict of replacements
    """
    return template.render(**ctx).encode("utf-8")

  def render_subject(self, context):
    """
    """
    return self._render(self.subject_template, context)

  def render_body_text(self, context):
    """
    """
    return self._render(self.body_text_template, context)

  def render_body_html(self, context):
    """
    """
    return self._render(self.body_html_template, context)


class DeliveryMethod(object):
  """
  enum for the different methods to send a message.
  """
  #:
  FLASKFLASH = 10
  #:
  SMS = 20
  #:
  GAEXMPP = 30
  #:
  GAEMAIL = 31
  #:
  SENDGRID = 50


class Message(object):
  """
  base class for a mesasage to send.

    :param template: instance of a `MessageTemplateMixin` subclass
  """
  def __init__(self, template):
    self.template = template

  def subject(self, context):
    return self.template.render_subject(context)

  def body_html(self, context):
    return self.template.render_body_html(context)

  def body_text(self, context):
    return self.template.render_body_text(context)

  def deliver(
    self, receiver, sender=None, in_reply_to=None, references=None,
    method=DeliveryMethod.GAEMAIL, as_task=True, taskqueue=TASKQUEUE_NAME,
    **context):
    """
    deliver message to a recipient.

      :param receiver: string address of the recipient
      :param sender: string address of the sender
      :param in_reply_to: string id of a conversation thread to reference
      :param references: reference of a conversation thread
      :param method: enum of the DeliveryMethod to transport a message
      :param as_task: boolean flag to send through app engine's taskqueue api
      :param taskqueue: string for the taskqueue name
      :param **context: dict of replacements to set for the message being sent,
        if one or more required paramaters for the template specified is
        missing, raises a `ValueError`
    """
    if sender is None:
      sender = self.template.sender

    transporter = method_to_transporter_mapping[method]()
    rv = MessageTransport(
      sender=sender,
      receiver=receiver,
      subject=self.template.render_subject(context),
      body_text=self.template.render_body_text(context),
      body_html=self.template.render_body_html(context),
      in_reply_to=in_reply_to,
      references=references,
      context=context,
      as_task=as_task,
      taskqueue=taskqueue)

    # dispatch signal event hook..
    if _signals:
      delivery_dispatched.send(rv, transporter=transporter)

    if as_task:
      deferred.defer(transporter.send, rv, _queue=taskqueue)
    else:
      transporter.send(rv)


class MessageTransport(object):
  """
  class for a captured result of a message delivery dispatch.

    :param sender: string address of the sender
    :param receiver: string address of the recipient
    :param subject: string subject of the message
    :param body_text: string plain text body of the message
    :param body_html: string html body of the message
    :param in_reply_to: string id of a conversation thread to reference
    :param references: reference of a conversation thread
    :param context:  dict of replacements to set for the message being sent
    :param as_task: boolean flag to send through app engine's taskqueue api
    :param taskqueue: string name of the taskqueue
  """
  def __init__(
    self, sender, receiver, subject, body_html, body_text,
    in_reply_to, references, context, as_task, taskqueue):
    self.sender = sender
    self.receiver = receiver
    self.subject = subject
    self.body_html = body_html
    self.body_text = body_text
    self.in_reply_to = in_reply_to
    self.references = references
    self.context = context
    self.as_task = as_task
    self.taskqueue = taskqueue


class MessageTransporter(object):
  """
  abstract class interface to transport a message.
  """

  def send(self, message_transport):
    """
      :param message_transport: instance of a `MessageTransport`
    """
    # dispatch signal event hook..
    if _signals:
      delivery_sent.send(message_transport, transporter=self)


class GAEMailMessageTransporter(MessageTransporter):
  """
  send messages through google app engine's mail api.
  """
  @classmethod
  def transport(cls, message):
    # MessageTransporter.send(self, message)
    try:
      headers = {}
      if message.in_reply_to:
        headers["In-Reply-To"] = message.in_reply_to
      if message.references:
        headers["References"] = message.references
      rv = mail.EmailMessage(
        to=message.to,
        sender=message.sender,
        subject=message.subject,
        body=message.body_text,
        html=message.body_html,
        headers=headers)
      rv.check_initialized()
      rv.send()
      return rv
    except:
      import traceback as tb
      logging.exception(
        "exception sending message through app engine mail api: %s",
        tb.format_ext())


class GAEXMPPMessageTransporter(MessageTransporter):
  """
  send a message through google app engine's xmpp api.
  """
  def send(self, message):
    MessageTransporter.send(self, message)
    raise NotImplemented()


class SendgridMessageTransporter(MessageTransporter):
  """
  """
  def send(self, message):
    MessageTransporter.send(self, message)
    raise NotImplemented()


class SMSMessageTransporter(MessageTransporter):
  """
  send a message through sms.
  """
  def send(self, message):
    MessageTransporter.send(self, message)
    raise NotImplemented()


class FlaskFlashMessageTransporter(MessageTransporter):
  """
  """
  def send(self, message):
    MessageTransporter.send(self, message)
    raise NotImplemented()


#:
method_to_transporter_mapping = {
  DeliveryMethod.FLASKFLASH: FlaskFlashMessageTransporter,
  DeliveryMethod.SMS: SMSMessageTransporter,
  DeliveryMethod.GAEMAIL: GAEMailMessageTransporter,
  DeliveryMethod.GAEXMPP: GAEXMPPMessageTransporter,
  DeliveryMethod.SENDGRID: SendgridMessageTransporter,
}


# signals event hooks..
if _signals:
  signals = blinker.Namespace()

  #:
  delivery_dispatched = signals.signal("delivery-dispatched", doc="""
  signal sent when a message delivery is dispatched.
  """)

  #:
  delivery_sent = signals.signal("delivery-sent", doc="""
  signal sent when a message delivery is sent. This signal will also be sent
  in testing mode, even though the message will not actually be sent.
  """)
