from datetime import datetime
from PrizeBondApp import db, login_manager
from flask_login.mixins import UserMixin
from time import time
import jwt
from flask import current_app as app

userbond = db.Table("userbond",
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True, nullable=False),
    db.Column('bond_id', db.Integer, db.ForeignKey('bond.id', ondelete="RESTRICT"), primary_key=True, nullable=False)
)

class Bond(db.Model):
    __tablename__ = 'bond'
    __table_args__ = (
        db.UniqueConstraint('bond_price_id', 'serial', name="unique_bond"),
    )
    id = db.Column(db.Integer, primary_key=True)
    bond_price_id = db.Column(db.Integer, db.ForeignKey('bondprice.id', ondelete='RESTRICT'), nullable=False)
    serial = db.Column(db.String(6), nullable=False)
    winning_bond = db.relationship("WinningBond", backref="bonds", lazy=True)

    def __repr__(self):
            return f"{self.serial}"
        
    def get_users(self):
        return self.user.all()
    
    def is_bond_holder(self, user):
        return self.user.filter(userbond.c.user_id == user.id).count() > 0


class Role(db.Model):
    __tablename__ = "role"
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20), index=True, unique=True, default="user" ,nullable=False)
    user = db.relationship("User", backref="role", lazy=True) 
    def __repr__(self):
        return f"{self.role}"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(120), nullable=False, index=True, unique=True)
    password = db.Column(db.String(60), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    confirmed = db.Column(db.Boolean, default=False, nullable=False)
    notifications = db.relationship('Notifications', backref='user', lazy='dynamic')
    # tasks = db.relationship('Tasks', backref='user', lazy='dynamic')
    bonds = db.relationship(
        "Bond", secondary=userbond,
        primaryjoin=(userbond.c.user_id == id),
        secondaryjoin=(userbond.c.bond_id == Bond.id),
        backref=db.backref("user", lazy='dynamic'), lazy='dynamic', cascade="all, delete")
    
    def __repr__(self):
        return f"Name: {self.name} Email: {self.email} Role: {self.role}"
    
    def add_bond(self, bond):
        self.bonds.append(bond)
    
    def remove_bond(self, bond):
        self.bonds.remove(bond)
    
    def get_bonds(self):
        return self.bonds.all()
    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {"reset_password": self.id, "exp": time() + expires_in},
            app.config["SECRET_KEY"], algorithm="HS256"
        )
    
    def add_notification(self, name, body):
        n = Notifications(name=name, body=body, user=self)
        db.session.add(n)
        return n
    
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config["SECRET_KEY"], algorithms="HS256")["reset_password"]
        except:
            return
        return User.query.get(id)
class BondPrice(db.Model):
    __tablename__ = 'bondprice'
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, index=True, unique=True, nullable=False)
    bond_prize = db.relationship("BondPrize", backref="price", lazy=True)
    bonds = db.relationship("Bond", backref="price", lazy=True)
    updated_lists = db.relationship("UpdatedLists", backref="price", lazy=True)
    drawdate = db.relationship("DrawDate", backref="price", lazy=True)

    def __repr__(self):
        return f"{self.price}"

class BondPrize(db.Model):
    __tablename__ = 'bondprize'
    __table_args__ = (
        db.UniqueConstraint("bond_price_id", "prize", name="unique_bond_prize"),
    )
    id = db.Column(db.Integer, primary_key=True)
    bond_price_id = db.Column(db.Integer, db.ForeignKey('bondprice.id', ondelete='CASCADE'), nullable=False)
    prize = db.Column(db.Integer, index=True, nullable=False, unique=True)    
    winning_bond = db.relationship("WinningBond", backref="prize", lazy=True)

    def __repr__(self):
        return f"{self.prize}"

class DrawDate(db.Model):
    __tablename__ = 'drawdate'
    __table_args__ = (
    db.UniqueConstraint('date', 'bond_price_id', name="unique_drawdate"),
)
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, index=True)
    bond_price_id = db.Column(db.Integer, db.ForeignKey("bondprice.id", ondelete="CASCADE"), nullable=False)
    winningbond = db.relationship("WinningBond", backref="date", lazy=True)
    updated_lists = db.relationship("UpdatedLists", backref="date", lazy=True)

    def __repr__(self):
        return f"{self.date}"

class UpdatedLists(db.Model):
    __tablename__ = "updatedlist"
    __table_args__ = (
    db.UniqueConstraint('date_id', 'bond_price_id', name="unique_bond_list"),
)
    id = db.Column(db.Integer, primary_key=True)
    date_id = db.Column(db.Integer, db.ForeignKey("drawdate.id", ondelete="CASCADE"), nullable=False)
    bond_price_id = db.Column(db.Integer, db.ForeignKey("bondprice.id", ondelete="CASCADE"), nullable=False)
    uploaded = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"{self.date_id} {self.bond_price_id}" 

class DrawLocation(db.Model):
    __tablename__ = "drawlocation"
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(20), nullable=False, index=True, unique=True)
    winningbond = db.relationship("WinningBond", backref="location", lazy=True)
    
    def __repr__(self):
        return f"{self.location}"

class DrawNumber(db.Model):
    __tablename__ = "drawnumber"
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False, unique=True)
    winningbond = db.relationship("WinningBond", backref="number", lazy=True)
    
    def __repr__(self):
        return f"{self.number}"
        
class WinningBond(db.Model):
    __tablename__ = 'winningbond'
    __table_args__ = (
        db.UniqueConstraint('bond_id', 'bond_prize_id', 'date_id', name="unique_bond_winner"),
    )
    id = db.Column(db.Integer, primary_key=True)
    bond_id = db.Column(db.Integer, db.ForeignKey('bond.id', ondelete="RESTRICT"), nullable=False)
    bond_prize_id = db.Column(db.Integer, db.ForeignKey('bondprize.id', ondelete="RESTRICT"), nullable=False)
    date_id = db.Column(db.Integer, db.ForeignKey('drawdate.id', ondelete="RESTRICT"), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey("drawlocation.id", ondelete="RESTRICT"), nullable=False)
    draw_id = db.Column(db.Integer, db.ForeignKey("drawnumber.id", ondelete="RESTRICT"), nullable=False)

    def __repr__(self):
            return f"BondId: {self.bond_id} BondPrizeId: {self.bond_prize_id} Date: {self.date}"   

class Notifications(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    timestamp = db.Column(db.Float, index=True, default=time)
    read = db.Column(db.Boolean, default=False)
    body = db.Column(db.String(200))

    def get_body(self):
        return str(self.body)
