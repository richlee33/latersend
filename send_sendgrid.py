import sendgrid
import os

# get sendgrid user and key from environment vars
api_user =  os.environ.get('SENDGRID_USER')
api_key =  os.environ.get('SENDGRID_KEY')
 
sg = sendgrid.SendGridClient(api_user, api_key)


def send(d):
    result = []
    message = sendgrid.Mail()
 
    message.add_to(d['recipient'])
    message.set_from(d['sender'])
    message.set_subject(d['subject'])
    message.set_html(d['message'])
 
    status, msg = sg.send(message)
    result = status

    return result

