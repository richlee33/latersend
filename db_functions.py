import sqlite3
import datetime

# configuration
DATABASE = '/temp/sqlite.db'

def connect_db():
    return sqlite3.connect(DATABASE)

def todays_emails():
    result = []
    db = connect_db()
    today = str(datetime.date.today())

    cur = db.execute('''select id, sender, recipient, subject, message, entry_date, send_date, sent from emails where send_date = ? and sent = ?''', (today, 0))
    emails_to_send = [dict(id=row[0], sender=row[1], recipient=row[2], subject=row[3], message=row[4], entry_date=row[5], send_date=row[6], sent=row[7]) for row in cur.fetchall()]

    result = emails_to_send

    db.close()

    return result

def update_sent_status(d,i):
    result = []
    db = connect_db()
    cur = db.execute('''UPDATE emails SET sent = ? WHERE id = ? ''', (i, d['id']))
    cur = db.commit()
    db.close()
    return result


#r = todays_emails()
#print r

#get the current date
#open a db connection
#select emails with send_date = current date and sent=0
#format data into sendgrid API
#submit data to sendgrid
#update emails that were sent to sent=1
#close the db connection
