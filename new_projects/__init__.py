from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
import os


app = Flask(__name__)
app.config['SECRET_KEY']='horathikxa'

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'postgresql://kura_kani_zmf0_user:JgtuyTcDlCYoam6ezjbFpDaqPm59bLeX@dpg-d2q1sjmr433s73dqc4dg-a.singapore-postgres.render.com/kura_kani_zmf0'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db=SQLAlchemy(app)
bcrypt=Bcrypt(app)
migrate = Migrate(app, db)
login_manager=LoginManager(app)
login_manager.login_view='login'
login_manager.login_message_category='info'

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=587
app.config['MAIL_USE_TLS']=True
app.config['MAIL_USERNAME']=os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD']=os.environ.get('EMAIL_PASS')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('EMAIL_USER')
app.config['DEBUG']=True
mail=Mail(app)  


from new_projects import routes
from new_projects import models