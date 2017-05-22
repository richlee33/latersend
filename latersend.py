# all the imports
import sqlite3
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
import datetime
from wtforms import Form, IntegerField, TextField, TextAreaField, validators

# configuration
DATABASE = '/tmp/sqlite.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'


# create our little application :)
app = Flask(__name__)

# import settings from settings file
#app.config.from_envvar('LATERSEND_SETTINGS', silent=True)

app.config.from_object(__name__)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

class EmailMessageForm(Form):
    sender = TextField('From:', [validators.required(), validators.Length(min=1, max=75), validators.Email()])
    recipient = TextField('To:', [validators.required(), validators.Length(min=1, max=75), validators.Email()])
    subject = TextField('Subject:', [validators.required(), validators.Length(min=1, max=35)])
    message = TextAreaField('Message:', [validators.required(), validators.Length(min=1, max=500)])
    days_ahead = IntegerField('Send in how many days:', [validators.required()])

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/emails', methods = ['GET', 'POST'])
def show_emails():
    if not session.get('logged_in'):
        abort(401)
    form = EmailMessageForm(request.form)
    if request.method == 'POST' and form.validate():
        today = datetime.date.today()
        if int(form.days_ahead.data) < 0:
            send_date = today
        else: 
            send_date = today + datetime.timedelta(days=int(form.days_ahead.data))

        g.db.execute('insert into emails(sender, recipient, subject, message, entry_date, send_date, sent) values (?, ?, ?, ?, ?, ?, ?)', [form.sender.data, form.recipient.data, form.subject.data, form.message.data, today, send_date, 0])
        g.db.commit()
        flash('New email was successfully saved')
        return redirect(url_for('show_emails'))

    cur = g.db.execute('select id, sender, recipient, subject, message, entry_date, send_date, sent from emails order by id desc')
    emails = [dict(id=row[0], sender=row[1], recipient=row[2], subject=row[3], message=row[4], entry_date=row[5], send_date=row[6], sent=row[7]) for row in cur.fetchall()]
    return render_template('show_emails.html', emails=emails, form = form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_emails'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True, ssl_context=('/home/richard/certs/server.crt', '/home/richard/certs/server.key'))
