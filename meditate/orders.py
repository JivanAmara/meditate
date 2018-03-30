import os
import email
import logging
import smtplib
from meditate.models import Order
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

def send_alert(report, user="", password="", send=True):
    # s = smtplib.SMTP(host='smtp.gmail.com', port=587)
    s = smtplib.SMTP('smtp.gmail.com:587')
    s.ehlo()
    s.starttls()
    s.login(user, password)

    msg = email.mime.multipart.MIMEMultipart()       # create a message

    # setup the parameters of the message
    msg['From']='jivan@jivanamara.net'
    msg['To']='jivan@jivanamara.net'
    msg['Subject']='Unprocessed Orders'

    # add in the message body
    msg.attach(email.mime.text.MIMEText(report, 'plain'))

    # send the message via the server set up earlier.
    if send:
        s.send_message(msg)
    del msg

    return True


def unprocessed_order_report():
    unprocessed_orders = Order.objects.filter(processed=False).exclude(paymentId=None)
    context = {"orders": unprocessed_orders}
    report = render_to_string("order_report.txt", context)

    report_lines = report.split('\n')
    for i, l in enumerate(report_lines):
        report_lines[i] = l.rstrip()
    treport = '\n'.join(report_lines)

    return treport
