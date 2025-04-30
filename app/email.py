from flask import current_app
from flask_mail import Message
from threading import Thread
from app import mail


def send_email_async(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(
        subject=subject,
        recipients=recipients,
        sender=sender,
        body=text_body,
        html=html_body,
    )
    # mail.send(msg) #!synchronous! = slows down the app
    Thread(target=send_email_async, args=(current_app._get_current_object(), msg)).start()
