from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)

# Configurations
app.config['SECRET_KEY'] = '8269ce5e81803447f884141f3057985ff4f58032687d16463a35790ee1528728'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# Database instance
db = SQLAlchemy(app)

# Bcrypt instance
bcrypt = Bcrypt(app)

# Login manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Routes
from flaskblog import routes