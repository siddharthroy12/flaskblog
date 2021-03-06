import os, dotenv, smtplib, ssl
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_ckeditor import CKEditor

app = Flask(__name__)

# Load .env file
dotenv.load_dotenv()

# Configurations
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

# Ckeditor
ckeditor = CKEditor(app)

# Heroku postgres for production
if os.environ.get('ENV') == "production":
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///demo'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Database instance
db = SQLAlchemy(app)

# Bcrypt instance
bcrypt = Bcrypt(app)

# Login manager
login_manager = LoginManager(app)
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'

port = 465  # For SSL
password = os.environ['EMAIL_PASSWORD']
        
# Create a secure SSL context
context = ssl.create_default_context()
email_server = smtplib.SMTP_SSL("smtp.gmail.com", port, context=context)
email_server.login(os.environ['EMAIL'], password)

# Routes
from flaskblog.users.routes import users
app.register_blueprint(users)
from flaskblog.posts.routes import posts
app.register_blueprint(posts)
from flaskblog.main.routes import main
app.register_blueprint(main)
from flaskblog.errors.handlers import errors
app.register_blueprint(errors)