flask-telegram
==============

[flask](http://flask.pocoo.org) extension for delivering messages.

send using [google app-engine](http://appengine.google.com) `mail` or `xmpp` apis,
and/or other third party providers such as [sendgrid](http://sendgrid.com)


<br>
**build-status:**

`master ` [![travis-ci build-status: master](https://secure.travis-ci.org/gregorynicholas/flask-telegram.svg?branch=master)](https://travis-ci.org/gregorynicholas/flask-telegram)
<br>
`develop` [![travis-ci build-status: develop](https://secure.travis-ci.org/gregorynicholas/flask-telegram.svg?branch=develop)](https://travis-ci.org/gregorynicholas/flask-telegram)


**links:**

* [homepage](http://gregorynicholas.github.io/flask-telegram)
* [source](http://github.com/gregorynicholas/flask-telegram)
* [python-package](http://packages.python.org/flask-telegram)
* [github-issues](https://github.com/gregorynicholas/flask-telegram/issues)
* [changelog](https://github.com/gregorynicholas/flask-telegram/blob/master/CHANGES.md)
* [travis-ci](http://travis-ci.org/gregorynicholas/flask-telegram)


<br>
-----
<br>


### getting started


install with pip:

    $ pip install flask-telegram


<br>
-----
<br>


### features

* [todo]


<br>
-----
<br>


### example usage

setup from outside the flask app request context:

    from flask.ext import telegram

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
      message.deliver(recipient=recipient, **context)



setup from within the flask app request context:

    [todo]
