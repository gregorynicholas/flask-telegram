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
  import dev_appserver
  dev_appserver.fix_sys_path()
except ImportError:
  pass

_has_signals = False
try:
  import blinker
  _has_signals = True
except ImportError:
  _has_signals = False

from flask import current_app
from logging import getLogger
from google.appengine.api import mail
from google.appengine.ext import deferred


__all__ = [
  "MessageTemplateMixin", "Message", "TransportProviders", "init_app",
  "register_transport_provider"]
logger = getLogger(__name__)


class MissingBodyTemplateError(ValueError):
  """
  """


class MessageTemplateMixin(object):
  """
  mixin class for the data model representing message templates.

    :param sender: string address of the sender
    :param subject_template: instance of a `jinja2.Template`
    :param body_html_template: instance of a `jinja2.Template`
    :param body_text_template: instance of a `jinja2.Template`
    :param jinja_env: instance of `jinja2.Environment`
    :param context: template context
  """

  def __init__(
    self, sender, subject_template, body_html_template, body_text_template,
    jinja_env=None, context=None):
    """
      :param sender: string address of the sender
      :param subject: string name of a `jinja2.Template`
      :param body_html_template: string name of a `jinja2.Template`
      :param body_text_template: string name of a `jinja2.Template`
      :param jinja_env: instance of `jinja2.Environment`
      :param context: template context
    """
    flaskapp = current_app._get_current_object()
    template_folder = flaskapp.config.get("telegram_template_folder", "")

    self.jinja_env = jinja_env or flaskapp.jinja_env
    self.context = context or {}
    self._sender = sender
    self._subject_template = template_folder + subject_template
    self._body_html_template = template_folder + body_html_template
    self._body_text_template = template_folder + body_text_template

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
    return self.jinja_env.get_template(self._subject_template)

  @property
  def body_html_template(self):
    """
      :returns: instance of `jinja2.Template`
    """
    return self.jinja_env.get_template(self._body_html_template)

  @property
  def body_text_template(self):
    """
      :returns: instance of `jinja2.Template`
    """
    return self.jinja_env.get_template(self._body_text_template)

  def _render(self, template, ctx):
    """
    calls the render method on a jinja2 template, and returns the result.

      :param template: instance of `jinja2.Template`
      :param ctx: dict of replacements
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


class TransportProviders(object):
  """
  enum for the different services to send a message.
  """
  #:
  FLASKFLASH = "flaskflash"


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
    provider=None, **context):
    """
    deliver message to a recipient.

      :param receiver: string address of the recipient
      :param sender: string address of the sender
      :param in_reply_to: string id of a conversation thread to reference
      :param references: reference of a conversation thread
      :param provider: enum of the TransportProviders to transport a message
      :param **context: dict of replacements to set for the message being sent,
        if one or more required paramaters for the template specified is
        missing, raises a `ValueError`
    """
    if sender is None:
      sender = self.template.sender

    # get config values defined in the flask app..
    flaskapp = current_app._get_current_object()
    #: boolean flag to send through app engine's taskqueue api
    send_as_task = flaskapp.config["telegram_send_as_task"]

    # merge the contexts..
    ctx = {}
    ctx.update(flaskapp.config["telegram_context"])
    ctx.update(self.template.context)
    ctx.update(context)

    if not provider:
      provider = flaskapp.config["telegram_transport_provider"]

    transporter = load_transport_provider(provider)
    msgtransport = MessageTransport(
      sender=sender,
      receiver=receiver,
      subject=self.subject(ctx),
      body_text=self.body_text(ctx),
      body_html=self.body_html(ctx),
      in_reply_to=in_reply_to,
      references=references)

    logger.debug(
      "telegram.deliver: receiver: %s, sender: %s, ctx: %s, "
      "transorter: %s, msgtransport: %s",
      receiver, sender, ctx, transporter, msgtransport)

    # dispatch signal event hook..
    if _has_signals:
      delivery_dispatched.send(msgtransport, transporter=transporter)

    if send_as_task:
      #: string name of the taskqueue
      taskqueue_name = flaskapp.config["telegram_taskqueue_name"]
      deferred.defer(transporter, msgtransport, _queue=taskqueue_name)
    else:
      transporter(msgtransport)


class MessageTransport(object):
  """
  class for a captured result of a message delivery.

    :param sender: string address of the sender
    :param receiver: string address of the recipient
    :param subject: string subject of the message
    :param body_text: string plain text body of the message
    :param body_html: string html body of the message
    :param in_reply_to: string id of a conversation thread to reference
    :param references: reference of a conversation thread
  """
  def __init__(
    self, sender, receiver, subject, body_html, body_text,
    in_reply_to, references):
    self.sender = sender
    self.receiver = receiver
    self.subject = subject
    self.body_html = body_html
    self.body_text = body_text
    self.in_reply_to = in_reply_to
    self.references = references


class TransportProvider(object):
  """
  base class to transport a message.
  """
  name = ""

  def __call__(self, msgtransport):
    """
      :param msgtransport: instance of a `MessageTransport`
    """
    # dispatch signal event hook..
    if _has_signals:
      delivery_sent.send(msgtransport, transporter=self)
    self.send(msgtransport)

  def send(self, msgtransport):
    """
      :param msgtransport: instance of a `MessageTransport`
    """
    raise NotImplementedError("subclass must implement the send method.")


#:
transport_providers = {}


def register_transport_provider(provider):
  """
    :param provider: instance of a `TransportProvider` subclass.
  """
  transport_providers[provider.name] = provider


def load_transport_provider(provider_name):
  """
    :param provider_name: string name of the transport provider.
  """
  if provider_name in transport_providers:
    return transport_providers[provider_name]
  short_name = "flask_telegram_{}".format(provider_name)
  module_name = "flask.ext.telegram_{}".format(provider_name)
  rv = __import__(module_name, None, None, [short_name])
  for k, v in rv.__dict__.iteritems():
    if type(v) is type and (
      issubclass(v, TransportProvider) and v.name is provider_name):
      register_transport_provider(v)
      return v


def init_app(flaskapp, **config):
  """
  configures a flask application.

    :param flaskapp:
    :param config:
  """
  template_folder = "{}{}".format(
    flaskapp.config.get("template_folder", ""),
    config.pop("template_folder", ""))
  flaskapp.config.setdefault("telegram_template_folder", template_folder)
  flaskapp.config.setdefault("telegram_context", {})
  flaskapp.config.setdefault("telegram_send_as_task", True)
  flaskapp.config.setdefault("telegram_taskqueue_name", "default")
  flaskapp.config.setdefault("telegram_transport_provider", "gaemail")
  for k, v in config.iteritems():
    flaskapp.config.setdefault("telegram_" + k, v)


# signals event hooks..
if _has_signals:
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
