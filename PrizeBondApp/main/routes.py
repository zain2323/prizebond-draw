from flask import Blueprint, render_template, url_for, redirect, flash
from flask_login.utils import current_user

main = Blueprint("main", __name__)

@main.route("/")
def home():
    if current_user.is_authenticated:
        if current_user.role.role == 'user':
            bonds = current_user.bonds.all()
            return render_template("main/home.html", bonds=bonds)
        elif current_user.role.role == 'administrator':
            return redirect(url_for("admin.index"))
    else:
        flash("Please login to access the page.", "info")
    return redirect(url_for("auth.sign_in"))