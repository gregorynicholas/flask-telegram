Flask App Engine Messages
======================================

Flask extension for working with messages using the mail & xmpp apis on App Engine.

Links
-----

* :ref:`genindex`
* `documentation <http://packages.python.org/flask-gae_messages>`_
* `source <http://github.com/gregorynicholas/flask-gae_messages>`_
* :doc:`changelog </changelog>`

Installing flask-gae_messages
------------------------------

Install with **pip**

`pip install https://github.com/gregorynicholas/flask-gae_messages/tarball/master`




API
---

.. module:: flask_gae_messages

.. autoclass:: MessageTemplate
   :members: sender, subject, template_html, template_text

.. autoclass:: Method

   .. autoattribute: currentmodule

   .. autoattribute: SMS
   .. autoattribute: XMPP
   .. autoattribute: EMAIL
   .. autoattribute: FLASH



.. autoclass:: Message

   .. automethod:: send(to, context, method=Method.EMAIL)


.. autofunction:: queue

.. autofunction:: send_mail

