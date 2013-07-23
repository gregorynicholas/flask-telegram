flask-telegram
==============

`Flask`_ extension for delivering messages. send via google's `App Engine`_
mail or xmpp apis, and/or other third party providers such as `Sendgrid`_.


links
-----

* :ref:`genindex`
* `documentation <http://gregorynicholas.github.io/flask-telegram>`_
* `package <http://packages.python.org/flask-telegram>`_
* `source <http://github.com/gregorynicholas/flask-telegram>`_
* `travis-ci <http://travis-ci.org/gregorynicholas/flask-telegram>`_
* :doc:`changelog </changelog>`


getting started
---------------

install with *pip*:

    pip install flask-telegram


example usage
-------------

    `from flask.ext import telegram

    # setup the jinja templates + environment..
    from jinja2 import Environment, loaders

    jinjaenv = Environment(loader=loaders.DictLoader({
      "subject.html": "{{ var_subject }},"
      "body.html": "<html>{{ var_html_body }}</html>,"
      "body.text": "{{ var_text_body }},"
    }))

    # setup the template..
    messagetemplate = telegram.MessageTemplate(
      sender="sender@domain.com",
      subject="subject.html",
      body_html="body.html",
      body_text="body.html",
      jinja_env=jinjaenv)

    # now let's assume you want to batch message recipients..
    recipients = ["r1@domain.com", "r2@domain.com", "r3@domain.com"]

    for recipient in recipients:
      context = {
        "var_subject": "telegram'd subject",
        "var_html_body": "telegram'd html body",
        "var_text_body": "telegram'd text body"}

      message = telegram.Message(messagetemplate)
      message.deliver(recipient=recipient, **context)`


api
---

.. module:: flask_telegram


.. autoclass:: MessageTemplateMixin
   :members: sender, subject_template, body_html_template, body_text_template

   .. automethod:: __init__(sender, subject, body_html, body_text, jinja_env)
   .. automethod:: render_subject(context)
   .. automethod:: render_body_text(context)
   .. automethod:: render_body_html(context)


.. autoclass:: Message
   :members:

   .. automethod:: __init__(template)

   .. automethod:: deliver(recipient, sender, in_reply_to, method=Method.GAEMAIL, as_task=True, taskqueue=TASKQUEUE_NAME, **context)


.. autoclass:: MessageTransport
    :members: sender, recipient, subject, body_html, body_text, in_reply_to, references, context, as_task, taskqueue


.. autoclass:: MessageTransporter

   .. automethod:: send(message_transport)


.. autoclass:: FlaskFlashMessageTransporter

   .. automethod:: send(message_transport)


.. autoclass:: GAEMailMessageTransporter

   .. automethod:: send(message_transport)


.. autoclass:: GAEXMPPMessageTransporter

   .. automethod:: send(message_transport)


.. autoclass:: SendgridMessageTransporter

   .. automethod:: send(message_transport)


.. autoclass:: DeliveryMethod
   :members: FLASKFLASH, GAEXMPP, GAEMAIL, SENDGRID


----

.. _Flask: http://flask.pocoo.org
.. _App Engine: http://appengine.google.com
.. _Sendgrid: http://sendgrid.com
