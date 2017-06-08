# all the imports
import sqlite3
#from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify, make_response
import datetime
from wtforms import Form, IntegerField, TextField, TextAreaField, validators
from flask_security import login_required, http_auth_required, auth_token_required, \
     Security, RoleMixin, UserMixin, SQLAlchemyUserDatastore
from flask_sqlalchemy import SQLAlchemy


# create our little application :)
app = Flask(__name__)

app.config['DEBUG'] = True
app.config['USERNAME'] = 'admin'
app.config['PASSWORD'] = 'default'
app.secret_key = 'super secret key'
app.config['SECURITY_TRACKABLE'] = True
app.config['SECURITY_PASSWORD_HASH'] = 'pbkdf2_sha512'
app.config['SECURITY_PASSWORD_SALT'] = 'something_super_secret_change_in_production'
app.config['WTF_CSRF_ENABLED'] = False
app.config['SECURITY_TOKEN_MAX_AGE'] = 365*24*60*60*1000

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# import settings from settings file
#app.config.from_envvar('LATERSEND_SETTINGS', silent=True)

app.config.from_object(__name__)

# Create database connection object
db = SQLAlchemy(app)


class EmailMessageForm(Form):
    sender = TextField('From:', [validators.required(), validators.Length(min=1, max=75), validators.Email()])
    recipient = TextField('To:', [validators.required(), validators.Length(min=1, max=75), validators.Email()])
    subject = TextField('Subject:', [validators.required(), validators.Length(min=1, max=35)])
    message = TextAreaField('Message:', [validators.required(), validators.Length(min=1, max=500)])
    days_ahead = IntegerField('Send in how many days:', [validators.required()])


roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(),
                                 db.ForeignKey('auth_user.id')),
                       db.Column('role_id', db.Integer(),
                                 db.ForeignKey('auth_role.id')))


# A base model for other database tables to inherit
class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    modified_at = db.Column(db.DateTime, default=db.func.current_timestamp(),
                            onupdate=db.func.current_timestamp())


class Role(Base, RoleMixin):
    __tablename__ = 'auth_role'
    name = db.Column(db.String(80), nullable=False, unique=True)
    description = db.Column(db.String(255))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Role %r>' % self.name


class User(Base, UserMixin):
    __tablename__ = 'auth_user'
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    # Why 45 characters for IP Address ?
    # See http://stackoverflow.com/questions/166132/maximum-length-of-the-textual-representation-of-an-ipv6-address/166157#166157
    last_login_ip = db.Column(db.String(45))
    current_login_ip = db.Column(db.String(45))
    login_count = db.Column(db.Integer)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return '<User %r>' % self.email


class EmailMessage(Base):
    __tablename__ = 'emails'
    sender = db.Column(db.String(75), nullable=False)
    recipient = db.Column(db.String(75), nullable=False)
    subject = db.Column(db.String(35), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    entry_date = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    send_date = db.Column(db.DateTime, nullable=False)
    sent = db.Column(db.Boolean(), nullable=False)


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


# Helper to convert list of objects into list of dictionaries
def convert_list_dict(list_objects):
    new_list = []

    for item in list_objects:
        dictret = dict(item.__dict__)
        dictret.pop('_sa_instance_state', None)
        new_list.append(dictret)

    return new_list


# Create a user with this function
def create_user():
    user_datastore.create_user(email='test@example.com', password='test123')
    db.session.commit()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/emails', methods = ['GET', 'POST'])
@login_required
def show_emails():
    form = EmailMessageForm(request.form)
    if request.method == 'POST' and form.validate():
        today = datetime.date.today()
        if int(form.days_ahead.data) < 0:
            send_date = today
        else: 
            send_date = today + datetime.timedelta(days=int(form.days_ahead.data))

        new_email = EmailMessage(sender=form.sender.data, recipient=form.recipient.data, \
                    subject=form.subject.data, message=form.message.data, entry_date=today, \
                    send_date=send_date, sent=False)

        db.session.add(new_email)
        db.session.commit()
        flash('New email was successfully saved')
        return redirect(url_for('show_emails'))

    emails = EmailMessage.query.all()
    return render_template('show_emails.html', emails=emails, form = form)


# No more /login route since using flask-security login now


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('index'))


# API URIs below

@app.route('/api/1.0/emails', methods=['GET'])
@auth_token_required
def get_emails():
    result = EmailMessage.query.all()

    emails = convert_list_dict(result)

    return jsonify({'emails': emails})


@app.route('/api/1.0/emails/<int:email_id>', methods=['GET'])
@auth_token_required
def get_email_id(email_id):
    result = EmailMessage.query.filter_by(id = email_id).all()

    emails = convert_list_dict(result)

    if len(emails) == 0:
        abort(404)
    return jsonify({'emails': emails})


@app.route('/api/1.0/emails', methods=['POST'])
@auth_token_required
def create_email():

    if not request.json or not 'sender' in request.json or not 'recipient' in request.json \
    or not 'subject' in request.json or not 'message' in request.json or not 'days_ahead' in request.json:
        abort(400)

    today = datetime.date.today()
    if int(request.json['days_ahead']) < 0:
        send_date = today
    else:
        send_date = today + datetime.timedelta(days=int(request.json['days_ahead']))

    new_email = EmailMessage(sender = request.json['sender'], recipient = request.json['recipient'], \
                subject = request.json['subject'], message = request.json['message'], entry_date = today, \
                send_date = send_date, sent = False)

    db.session.add(new_email)
    db.session.commit()

    # get the lastest emailmessage object
    result = EmailMessage.query.order_by('-id').first()

    email = dict(result.__dict__)
    email.pop('_sa_instance_state', None)

    return jsonify({'email': email}), 201 


@app.route('/api/1.0/emails/<int:email_id>', methods=['DELETE'])
@auth_token_required
def delete_email(email_id):
    status = EmailMessage.query.filter_by(id = email_id).delete()
    db.session.commit()

    if status == 0:
        abort(404)

    return jsonify({'result': True}), 204


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    app.run(debug=True, ssl_context=('/home/richard/certs/server.crt', '/home/richard/certs/server.key'))
