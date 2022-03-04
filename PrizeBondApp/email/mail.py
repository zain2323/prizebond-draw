from flask_mail import Message
from PrizeBondApp import mail
from flask import render_template, current_app as app
from threading import Thread
from flask import flash
from functools import wraps

def production_mode(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if app.debug:
            flash("Not sending email due to in debugging mode.", "info")
        else:
            func(*args, **kwargs)
    return wrapper

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body, sync=False, attachments=None):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    if attachments is not None:
        for attachment in attachments:
            msg.attach(*attachment)
    if sync:
        mail.send()
    else:
        Thread(target=send_async_email, args=(app._get_current_object(), msg)).start()

@production_mode
def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email("[PrizeBond] Reset your password",
    recipients=[user.email],
    sender=app.config["ADMINS"][0],
    text_body=render_template('email/reset_password_message.txt',
                                         user=user, token=token),
    html_body=render_template('email/reset_password_message.html',
                                         user=user, token=token))
@production_mode
def send_confirmation_email(user):
    token = user.get_reset_password_token()
    send_email("[PrizeBond] Confirm your email", 
    recipients=[user.email],
    sender=app.config["ADMINS"][0],
    text_body=render_template("email/confirmation_email.txt", user=user, token=token),
    html_body=render_template("email/confirmation_email.html", user=user, token=token))