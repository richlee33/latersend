latersend
========
compose an email now and at a later date, send the email.

how it works
------------
the app provides a form for composing an email.  once the
email is submitted, it is stored into an sqlite3 db.

there is a backend process that periodically checks the db 
for emails to send.
when the time comes to send an email, it uses the SAAS email
provider [SendGrid](https://github.com/sendgrid/sendgrid-python)
library to deliver the message.

this app is based on the [flaskr](https://github.com/mitsuhiko/flask/tree/master/examples/flaskr/)
 tutorial 

how to run it
-------------
clone repo  
`cd latersend`
`virtualenv . --no-site-packages`
`source bin/activate`
`pip install -r requirements.txt`

to run application
`python latersend.py`

to run backend process
`python latersend_backend.py`

to access application:
point your browser to http://127.0.0.1:5000

