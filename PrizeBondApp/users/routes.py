from os import abort
from PrizeBondApp.email.mail import send_confirmation_email
from PrizeBondApp.utils import UtilityFunctions
from flask_login.utils import login_required, current_user
from PrizeBondApp import db, bcrypt
from flask import json, render_template, url_for, redirect, flash, request, Blueprint, abort, jsonify
from PrizeBondApp.users.forms import AddBond, AddBondSeries, EmailForm, NameForm, PasswordForm, ResultsForm
from PrizeBondApp.models import Bond, BondPrice, DrawDate, Notifications, User, WinningBond
from functools import wraps
from PrizeBondApp.users import admin
from sqlalchemy import func


users = Blueprint("users", __name__)

def confirm_user_required(func):
    @wraps(func)
    def wrappper(*args, **kwargs):
        if current_user.role.role == "user" and current_user.confirmed:
            return func(*args, **kwargs)
        else:
            flash("You can not access the page because your email is not confirmed.", "warning")
            return redirect(url_for("main.home"))
    return wrappper


@users.route("/add_bond", methods=["GET", "POST"])
@login_required
@confirm_user_required
def add_bond(denomination=None, serial=None):
    form = AddBond()
    form.denomination.choices = UtilityFunctions.load_denominations()
    if form.validate_on_submit():
        denomination = int(form.denomination.data)
        serials = form.serial.data
        serials = UtilityFunctions.normalize_serials(serials)
        bond_price = BondPrice.query.filter_by(price=denomination).first()
        for serial in serials:
            bond_db = Bond.query.filter_by(serial=serial, price=bond_price).first()
            if bond_db:
                if not bond_db.is_bond_holder(current_user):
                    current_user.add_bond(bond_db)
                    db.session.commit()
                else:
                    flash("You have already added this bond", "info")
                    return redirect(url_for("users.add_bond"))
            else:
                bond = Bond(serial=serial, price=bond_price)
                db.session.add(bond)
                current_user.add_bond(bond)
                db.session.commit()
        flash("All bonds added successfully", "info")
        return redirect(url_for("users.add_bond"))
    return render_template("user/add_bond.html", form=form)

@users.route("/add_bond/range", methods=["GET", "POST"])
@login_required
@confirm_user_required
def add_bond_range():
    form = AddBondSeries()
    form.denomination.choices  = UtilityFunctions.load_denominations()
    if form.validate_on_submit():
        denomination = int(form.denomination.data)
        serial_start = form.serial_start.data
        serial_end = form.serial_end.data
        bond_price = BondPrice.query.filter_by(price=denomination).first()
        if serial_start <= serial_end:
            diff = abs(int(serial_end) - int(serial_start))
            for i in range(0, diff+1):
                serial =  str(int(serial_start) + i)
                serial = UtilityFunctions.append_leading_zeroes(serial_start, serial)
                bond_db = Bond.query.filter_by(serial=serial, price=bond_price).first()
                if bond_db:
                    if not bond_db.is_bond_holder(current_user):
                        current_user.add_bond(bond_db)
                        db.session.commit()
                    else:
                        flash("You have already added bond " + serial, "info")
                        return redirect(url_for("users.add_bond_range"))
                else:
                    bond = Bond(serial=serial, price=bond_price)
                    db.session.add(bond)
                    current_user.add_bond(bond)
            db.session.commit()
            flash("All bonds added successfully", "info")
        else:
            flash("Invalid range", "danger")
        return redirect(url_for("users.add_bond_range"))
    return render_template("user/range_serial.html", form=form)


@users.route("/remove_bond", methods=["GET", "POST"])
@login_required
@confirm_user_required
def remove_bond(denomination=None, serial=None):
    form = AddBond()
    form.denomination.choices = UtilityFunctions.load_denominations()
    if request.method == 'GET':
        denomination = request.args.get("denomination")
        serial = request.args.get("serial")
        if denomination and serial:
            serial = UtilityFunctions.normalize_serials(serial)[0]
            form.denomination.data = BondPrice.query.filter_by(price=int(denomination)).first().id
            form.serial.data = serial

    if form.validate_on_submit():
        denomination = int(form.denomination.data)
        serial = form.serial.data
        serial = UtilityFunctions.normalize_serials(serial)[0]
        # Fetching the bond from the database
        try:
            bond_price = BondPrice.query.filter_by(price=denomination).first()
            bond = Bond.query.filter_by(serial=serial, price=bond_price).first()
            if bond.is_bond_holder(current_user):
                current_user.remove_bond(bond)
                db.session.commit()
                flash("Bond deleted successfully.", "success")
            else:
                flash("No bond with the specified serial and domination exists.", "warning")
            return redirect(url_for("main.home"))
        except:
            flash("No bond with the specified serial and domination exists.", "warning")
            return redirect(url_for("main.home"))
    return render_template("user/remove_bond.html", form=form)


@users.route("/get_date", methods=["POST"])
@login_required
@confirm_user_required
def get_date():
    return jsonify({"denomination": UtilityFunctions.load_date(request.get_json()["denomination"])})

@users.route("/check_results", methods=["GET", "POST"])
@login_required
@confirm_user_required
def check_results():
    form = ResultsForm()
    form.denomination.choices = UtilityFunctions.load_denominations()
    entries = UtilityFunctions.load_user_bonds(current_user)
    try:
        choice = form.denomination.choices[0]
    except:
        choice = None
    form.date.choices = UtilityFunctions.load_date(choice)
    if form.validate_on_submit():
        denomination = int(form.denomination.data)
        serial = form.serial.data
        date = form.date.data
        isInt = False
        bond_date = DrawDate.query.filter(func.DATE(DrawDate.date) == date).first()
        if bond_date is None:
            flash("Please choose the valid date.", "error")
            return redirect(url_for("users.check_results"))
        bond_price = BondPrice.query.filter_by(price=denomination).first()
        if bond_price:
            try:
                val = int(serial)
                isInt = True
            except:
                val = serial.lower()
            
            if not isInt and val == 'check all':
                bonds = current_user.get_bonds()
                winning_bonds = []
                for bond in bonds:
                    winning_bond = bond.winning_bond
                    if len(winning_bond) > 0:
                        if winning_bond[0].date.id == bond_date.id and winning_bond[0].bonds.price.id == bond_price.id:
                            winning_bonds.append(winning_bond[0])
                if len(winning_bonds) > 0:
                    return render_template("user/results.html", bonds=winning_bonds)
                else:
                    flash("Better try next time", "info")
            else:
                bond = Bond.query.filter_by(serial=serial).first()
            
                if not bond:
                    flash("No bond exists with the specified serial.", "warning")
                    return redirect(url_for("users.check_results"))
                winning_bond = WinningBond.query.filter_by(bonds=bond, date_id=bond_date.id).all()
                if winning_bond and winning_bond[0].bonds.price.price == denomination:
                    return render_template("user/results.html", bonds=winning_bond)
                else:
                    flash("Better try next time", "info")
        return redirect(url_for("users.check_results"))
    return render_template("user/check_results.html", form=form, entries=entries)

@users.route("/account_info/<int:user_id>", methods=["GET", "POST"])
@login_required
# @confirm_user_required
def account_info(user_id):
    user = User.query.get(user_id)
    if not user:
        return abort(403)
    if current_user.id != user.id:
        return abort(403)
    bonds = current_user.get_bonds()
    bond_data = {}
    for bond in bonds:
        if str(bond.price) not in bond_data:
            bond_data[str(bond.price)] = 1
        else:
            bond_data[str(bond.price)] += 1

    return render_template("user/account_info.html", user=user, bond_data=bond_data)

@users.route("/account_info/<int:user_id>/name", methods=["GET", "POST"])
def account_name(user_id):
    user = User.query.get(user_id)
    if not user:
        return abort(403)
    if current_user.id != user.id:
        return abort(403)
    form = NameForm()
    old_name = str(user.name).capitalize()
    if form.validate_on_submit():
        new_name = form.new_name.data.lower()
        user.name = new_name
        db.session.commit()
        flash("Name updated successfully.", "success")
        return redirect(url_for("users.account_info", user_id=user.id))
    return render_template("user/account_name.html", form=form, old_name=old_name)

@users.route("/account_info/<int:user_id>/email", methods=["GET", "POST"])
def account_email(user_id):
    user = User.query.get(user_id)
    if not user:
        return abort(403)
    if current_user.id != user.id:
        return abort(403)
    form = EmailForm()
    old_email = user.email
    if form.validate_on_submit():
        new_email = form.new_email.data.lower()
        user.email = new_email
        user.confirmed = False
        db.session.commit()
        flash("Email updated successfully.", "success")
        if new_email != old_email:
            flash("Confirmation email has been sent. Please check your inbox for further details.", "warning")
            send_confirmation_email(user)
        return redirect(url_for("users.account_info", user_id=user.id))
    return render_template("user/account_email.html", form=form, old_email=old_email)

@users.route("/account_info/<int:user_id>/password", methods=["GET", "POST"])
def account_password(user_id):
    user = User.query.get(user_id)
    if not user:
        return abort(403)
    if current_user.id != user.id:
        return abort(403)
    form = PasswordForm()
    if form.validate_on_submit():
        current_password = form.current_password.data
        new_password = form.new_password.data
        if bcrypt.check_password_hash(user.password, current_password):
            user.password = bcrypt.generate_password_hash(new_password).decode("utf-8")
            db.session.commit()
            flash("Password updated successfully.", "success")
        else:
            flash("Incorrect password", "danger")
        return redirect(url_for("users.account_info", user_id=user.id))
    return render_template("user/account_password.html", form=form)

@users.route("/account_info/<int:user_id>/send_confirmation_email", methods=["GET", "POST"])
def account_confirmation_email(user_id):
    user = User.query.get(user_id)
    if not user:
        return abort(403)
    if current_user.id != user.id:
        return abort(403)
    if not user.confirmed:
        flash("Confirmation email has been sent. Please check your inbox for further details.", "warning")
        send_confirmation_email(user)
    else:
        flash("Already confirmed.", "info")
    return redirect(url_for("users.account_info", user_id=user.id))

@users.route("/get_notifications", methods=['GET', 'POST'])
@login_required
def get_notifications():
    notification = current_user.notifications.order_by(Notifications.timestamp.desc()).limit(5).all()
    payload = [{"id": n.id, "name": n.name, "body": n.body,
               "read": n.read, "timestamp": n.timestamp} for n in notification]
    return jsonify(payload)

@users.route("/read_notifications", methods=["POST"])
@login_required
def read_notifications():
    notifications = request.get_json("notification")
    for notification in notifications:
        id = notification["id"]
        n = Notifications.query.get(id)
        if n:
            n.read = True
    try:
        db.session.commit()
    except:
        db.session.rollback()
    return redirect(url_for("main.home"))

