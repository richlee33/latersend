latersend
========
compose an email now and at a later date, automatically send the 
email.


how it works
------------
the app provides a form for composing an email.  once the
email is submitted, it is stored into an sqlite3 db.

there is a backend process that periodically checks the db 
for emails to send.
when the time comes to send an email, it uses the SAAS email
provider [SendGrid](https://github.com/sendgrid/sendgrid-python)
library to deliver the message.

this app uses the python flask framework and is based on 
the [flaskr](https://github.com/mitsuhiko/flask/tree/master/examples/flaskr/)
 tutorial.  


how to run it
-------------
set up environment:  
`git clone <repo url>`  
`cd latersend`  
`virtualenv . --no-site-packages`  
`source bin/activate`  
`pip install -r requirements.txt`  

run application:  
`python latersend.py`  

run backend process:  
`python latersend_backend.py`  

access application:  
point your browser to https://127.0.0.1:5000  


other setup needed
------------------
* put your SendGrid user and key into the env vars
SENDGRID_USER and SENDGRID_KEY
* initialize sqlite3 db  
`python`  
`>>> from latersend import init_db`  
`>>> init_db()`  
* create development certificate and key to serve on https (more info at [akadia.com](https://www.akadia.com/services/ssh_test_certificate.html))

    generate a private key

        openssl genrsa -des3 -out server.key 1024

    generate a CSR

        openssl req -new -key server.key -out server.csr

    remove passphrase from key

        cp server.key server.key.org
        openssl rsa -in server.key.org -out server.key

    generate a self signed certificate

        openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt



