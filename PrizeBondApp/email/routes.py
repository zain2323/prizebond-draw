from PrizeBondApp.email.mail import send_password_reset_email
from flask_login.utils import current_user
from PrizeBondApp import db, bcrypt
from flask import render_template, url_for, redirect, flash, Blueprint
from PrizeBondApp.email.forms import ResetPasswordRequestForm, ResetPasswordForm
from PrizeBondApp.models import User

email = Blueprint("email", __name__)

@email.route("/reset_password_request", methods=["GET", "POST"])
def reset_password_request():
    if current_user.is_authenticated:
        flash("No need to reset, you are already logged in.", "info")
        return redirect(url_for("main.home"))
    
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            send_password_reset_email(user)
        flash("Check your email for further instructions to reset your password.", "info")
        return redirect(url_for("auth.sign_in"))
    return render_template("email/reset_password_request.html", form=form)

@email.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.home'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user.password = hashed_pw
        db.session.commit()
        flash('Your password has been reset.', "success")
        return redirect(url_for('auth.sign_in'))
    return render_template('email/reset_password.html', form=form)

@email.route("/confirm_email/<string:token>", methods=["GET", "POST"])
def confirm_email(token):
    user = User.verify_reset_password_token(token)
    if not user:
        flash("Invalid request.", "danger")
        return redirect(url_for("main.home"))
    user.confirmed = True
    db.session.commit()
    flash("Your email has been confirmed.", "success")
    return redirect(url_for("main.home")) 
