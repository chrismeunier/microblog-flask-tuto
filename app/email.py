from flask import render_template
from flask_mail import Message
from app import mail, app
from app.models import User


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(
        subject=subject,
        recipients=recipients,
        sender=sender,
        body=text_body,
        html=html_body,
    )
    mail.send(msg)


def send_password_reset_email(user: User):
    token = user.get_reset_password_token()
    send_email(
        "[Microblog] Reset Your Password",
        sender=app.config["ADMINS"][0],
        recipients=[user.email],
        text_body=render_template("email/reset_password.txt", user=user, token=token),
        html_body=render_template("email/reset_password.html", user=user, token=token),
    )
