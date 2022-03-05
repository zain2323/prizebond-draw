from flask import Flask
from flask_admin.base import AdminIndexView
import flask_login
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_admin import Admin
from flask_mail import Mail
from PrizeBondApp.config import ProductionConfig as Config
import logging
from logging.handlers import RotatingFileHandler, SMTPHandler
from pathlib import Path


# db = SQLAlchemy(session_options={"autoflush": False})
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
login_manager.login_view = "auth.sign_in"
login_manager.login_message_category = "info"
admin = Admin()
mail = Mail()

def create_app(config=Config):
    # Restricting the admin panel index route
    class RestrictIndexView(AdminIndexView):
        def is_accessible(self):
            return flask_login.current_user.is_authenticated and flask_login.current_user.role.role == 'administrator'
    
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    admin.init_app(app, index_view=RestrictIndexView())
    mail.init_app(app)
    
    from PrizeBondApp.main.routes import main
    from PrizeBondApp.auth.routes import auth
    from PrizeBondApp.email.routes import email
    from PrizeBondApp.users.routes import users
    from PrizeBondApp.errors.handlers import errors
    
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(email)
    app.register_blueprint(users)
    app.register_blueprint(errors)
    
    # Logging setup for sending emails
    if not app.debug:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='PrizeBond Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        if not Path("logs").exists():
            Path("logs").mkdir()
            file_handler = RotatingFileHandler('logs/prizebond.log', maxBytes=2000000,
                                            backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.DEBUG)
            app.logger.addHandler(file_handler)

            app.logger.setLevel(logging.DEBUG)
            app.logger.info('PrizeBond startup')

    return app