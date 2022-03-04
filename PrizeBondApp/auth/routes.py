from flask import Blueprint, redirect, render_template, url_for, flash, request
from flask_login.utils import current_user, login_user, logout_user
from PrizeBondApp.email.mail import send_confirmation_email
from PrizeBondApp.models import Role, User
from PrizeBondApp import db, bcrypt
from PrizeBondApp.auth.forms import SignUpForm, SignInForm

auth = Blueprint("auth", __name__)

@auth.route("/signUp", methods=['GET', 'POST'])
def sign_up():
    form = SignUpForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        name = form.name.data.lower()
        email = form.email.data.lower()
        password = hashed_pw
        user_role = "user"
        if email == 'admin@admin.com':
            user_role = 'administrator'
        role = Role.query.filter_by(role=user_role).first()
        if role is None:
            role = Role(role=user_role)
            db.session.add(role)
            db.session.commit()
        user = User(name=name, email=email, password=password, role_id=role.id)
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created successfully! You can now login.", 'success')
        return redirect(url_for('auth.sign_in'))
    return render_template("auth/signUp.html", title='Register', form=form)

@auth.route("/")
@auth.route("/signIn", methods=['GET', 'POST'])
def sign_in():
    form = SignInForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            if not user.confirmed:
                flash("Confirmation email has been sent. Please check your inbox for further details.", "warning")
                send_confirmation_email(user)
            else:
                flash("Login Successfull!", "success")
            if form.email.data == "admin@admin.com" and current_user.role.role == "administrator":
                return redirect(url_for("admin.index"))
            # If the user tries to access some route that requires login then
            # this line of code stores the url of that route and redirects the user
            # to that url after he has logged in successfully.
            next = request.args.get('next')
            return redirect(next or url_for('main.home'))
        else:
            flash("Please check your email or password.", "danger")
        return redirect(url_for('auth.sign_in'))
    return render_template("auth/signin.html", title='Login', form=form)


@auth.route("/signOut", methods=['GET', 'POST'])
def sign_out():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect(url_for("auth.sign_in"))