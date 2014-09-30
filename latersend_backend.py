import sys
import db_functions 
import send_sendgrid
import time

while True:

    emails_to_send = db_functions.todays_emails()

    if emails_to_send:
        for email in emails_to_send:
            status = send_sendgrid.send(email)
            if '200' in str(status):
                sys.stdout.write("S")  
                db_functions.update_sent_status(email,1) 
            else:
                sys.stdout.write("E")  
                db_functions.update_sent_status(email,3) 
    else:
        sys.stdout.write("_")  

    sys.stdout.flush()
    time.sleep(120)

