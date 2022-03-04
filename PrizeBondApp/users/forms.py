from flask_login.utils import current_user
from PrizeBondApp.models import BondPrice, BondPrize, DrawDate, User
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.fields.core import IntegerField, SelectField
from wtforms.fields.simple import SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Length, ValidationError, EqualTo
from flask_wtf.file import FileField, FileAllowed
from wtforms.fields.html5 import DateField
from wtforms.fields import TextAreaField
from PrizeBondApp.utils import UtilityFunctions
from sqlalchemy import func


# Validator that checks every field is free from slash (/) because this may cause error in some cases.
def check_slash(form, field):
    if "/" in field.data:
        raise ValidationError("\ is not allowed.")

def validate_serial(form, field):
    serial = field.data
    if not serial.isdigit():
            raise ValidationError("Invalid serials")
    if len(serial) != 6:
            raise ValidationError("Serials must contain exactly six digits.")

def validtate_serial_end(form, serial_end):
    print(serial_end.data)
    if form.serial_start.data > serial_end.data:
        raise ValidationError("Invalid range!")

class FileForm(FlaskForm):
    price = SelectField("Price", validators=[DataRequired()])
    prize = SelectField("Prize", validators=[DataRequired()])
    date = DateField("Draw Date", validators=[DataRequired()])
    location = StringField("Draw Location", validators=[DataRequired()])
    number = IntegerField("Draw Number", validators=[DataRequired()])
    name = FileField("Upload Results", validators=[DataRequired(), FileAllowed(["txt"])])
    submit = SubmitField("Upload")

    def validate_location(self, location):
        if location.data.isdigit():
            raise ValidationError("Invalid input!")

    def validate_prize(self, prize):
        bond_prize = BondPrize.query.filter_by(prize=prize.data).first()
        if not bond_prize:
            raise ValidationError("Please select the valid prize.")
    

class AddBond(FlaskForm):
    denomination = SelectField("Select Denomination")
    serial = TextAreaField("Serial No", validators=[DataRequired(), check_slash])
    submit = SubmitField("Add")

    def validate_serial(self, serial):
        serials = UtilityFunctions.normalize_serials(serial.data)
        for normalized_serial in serials:
            if not normalized_serial.isdigit():
                raise ValidationError("Invalid serials")
            if len(normalized_serial) != 6:
                raise ValidationError("Serials must contain exactly six digits.")

class AddBondSeries(FlaskForm):
    denomination = SelectField("Select Denomination")
    serial_start = StringField("From", validators=[DataRequired(), check_slash, validate_serial])
    serial_end = StringField("To", validators=[DataRequired(), check_slash, validate_serial, validtate_serial_end])
    submit = SubmitField("Add")

class NotificationForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), check_slash])
    body = TextAreaField("Message", validators=[DataRequired(), check_slash])
    submit = SubmitField("Send")

    
class WinningBondForm(FlaskForm):
    denomination = SelectField("Select Denomination")
    prize = SelectField("Prize")
    serial = TextAreaField("Serial No", validators=[DataRequired(), check_slash])
    date = DateField("Draw Date", validators=[DataRequired()])
    location = StringField("Draw Location", validators=[DataRequired()])
    number = IntegerField("Draw Number", validators=[DataRequired()])
    submit = SubmitField("Add")

    def validate_prize(self, prize):
        bond_prize = BondPrize.query.filter_by(prize=prize.data).first()
        if not bond_prize:
            raise ValidationError("Please select the valid prize.")
    
    def validate_location(self, location):
        if location.data.isdigit():
            raise ValidationError("Invalid input!")

    def validate_serial(self, serial):
        serials = UtilityFunctions.normalize_serials(serial.data)
        for normalized_serial in serials:
            if not normalized_serial.isdigit():
                raise ValidationError("Invalid serials")
            if len(normalized_serial) != 6:
                raise ValidationError("Serials must contain exactly six digits.")
    
    def validate_serial(self, serial):
        serials = UtilityFunctions.normalize_serials(serial.data)
        for normalized_serial in serials:
            if not normalized_serial.isdigit():
                raise ValidationError("Invalid serials")
            if len(normalized_serial) != 6:
                raise ValidationError("Serials must contain exactly six digits.")

class AddDenominationForm(FlaskForm):
    denomination = IntegerField("Denomination", validators=[DataRequired()])
    submit = SubmitField("Add")

    def validate_denomination(self, denomination):
        price = BondPrice.query.filter_by(price=denomination.data).first()
        if price:
            raise ValidationError("Denomination already exists.")

class AddDenominationPrizeForm(FlaskForm):
    denomination = SelectField("Select Denomination", validators=[DataRequired()])
    prize = IntegerField("Prize", validators=[DataRequired()])
    submit = SubmitField("Add")
    
    def validate_denomination(self, denomination):
        price = BondPrice.query.filter_by(price=denomination.data).first()
        if price is None:
            raise ValidationError("Denomination do not exists.")
    
    def validate_prize(self, prize):
        bond_price_id = BondPrice.query.filter_by(price=self.denomination.data).first().id
        prize = BondPrize.query.filter_by(prize=prize.data, bond_price_id=bond_price_id).first()
        if prize:
            raise ValidationError("This denomination prize already exists.")

class ValidationSelectField(SelectField):

    def pre_validate(self, form):
        pass

class ResultsForm(FlaskForm):
    denomination = SelectField("Select Denomination", validators=[DataRequired()])
    serial = StringField("Serial No", validators=[DataRequired(), check_slash])
    date = ValidationSelectField("Draw Date", validators=[DataRequired()])
    submit = SubmitField("Check")


    def validate_date(self, date):
        draw_date = DrawDate.query.filter(func.DATE(DrawDate.date == date.data)).first()
        bond_date = UtilityFunctions.load_date(self.denomination.data)
        if draw_date is None or date.data not in bond_date:
            raise ValidationError("Date is invalid!")
            
    def validate_denomination(self, denomination):
        price = BondPrice.query.filter_by(price=denomination.data).first()
        if price is None:
            raise ValidationError("Denomination do not exists.")
    
    def validate_serial(self, serial):
        isInt = False
        try:
            int(serial.data)
            isInt = True
        except:
            val = serial.data.lower() == "check all"
        if isInt:
            serials = UtilityFunctions.normalize_serials(serial.data)
            for normalized_serial in serials:
                if not normalized_serial.isdigit():
                    raise ValidationError("Invalid serials")
                if len(normalized_serial) != 6:
                    raise ValidationError("Serials must contain exactly six digits.")
        elif not isInt and not val:
            raise ValidationError("Invalid")

class NameForm(FlaskForm):
    old_name = StringField('Old Name')
    new_name = StringField('New Name', validators=[DataRequired(message="Name field can not be empty!"),
                                          Length(min=3, max=30), check_slash])  
    submit = SubmitField("Update")

class EmailForm(FlaskForm):
    old_email = StringField('Old Email')
    new_email = StringField('New Email', validators=[DataRequired(message="Email field can not be empty!"),
                                          Length(min=3, max=30), check_slash, Email()])  
    submit = SubmitField("Update")

    def validate_new_email(self, new_email):
        user = User.query.filter_by(email=new_email.data).first()
        if user and current_user.id != user.id:
            raise ValidationError("This email is already taken!")

class PasswordForm(FlaskForm):
    current_password = PasswordField("Current Password", validators=[DataRequired(message="Password field can not be empty!"),
                                            Length(min=8, max=60, message="Password length should be atleast 8 characters!"), check_slash])
    new_password = PasswordField("New Password", validators=[DataRequired(message="Password field can not be empty!"),
                                            Length(min=8, max=60, message="Password length should be atleast 8 characters!"), check_slash])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(message="Confirm password field can not be empty!"),
                                            EqualTo('new_password', message="Password mismatch"), check_slash])
    submit = SubmitField("Update")