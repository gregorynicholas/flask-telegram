"""
  flask.ext.telegram_gaemail
  ~~~~~~~~~~~~~~~~~~~~~~~~~~

  http://gregorynicholas.github.io/flask-telegram


  :copyright: (c) by gregorynicholas.
  :license: MIT, see LICENSE for more details.
"""
from flask.ext import telegram
from logging import getLogger
from google.appengine.api import mail

__all__ = ["GAEMailTransportProvider"]
logger = getLogger(__name__)


class GAEMailTransportProvider(telegram.TransportProvider):
  """
  send messages through google app engine's mail api.
  """
  name = "gaemail"

  def send(self, msgtransport):
    headers = None
    if msgtransport.in_reply_to:
      headers = {}
      headers["In-Reply-To"] = msgtransport.in_reply_to
    if msgtransport.references:
      headers = headers or {}
      headers["References"] = msgtransport.references

    rv = mail.EmailMessage(
      to=msgtransport.receiver,
      sender=msgtransport.sender,
      subject=msgtransport.subject,
      body=msgtransport.body_text,
      html=msgtransport.body_html)
      # see: https://code.google.com/p/googleappengine/source/browse/trunk/\
      # python/google/appengine/api/mail.py#295
      # the worst fucking line of code i've ever encountered..  why they
      # would perform argument validation in such a way is really beyond me
      # headers=headers)
    rv.check_initialized()
    rv.send()
    return rv


telegram.register_transport_provider(GAEMailTransportProvider)
