from flask import Flask

from routes.Users.Users_BP import Users_BP, Users
from routes.Posts.Posts_BP import Posts_BP
from routes.System.System_BP import System_BP
from flask_login import LoginManager

from flask import Flask
from extensions import db,migrate, ckeditor

app = Flask(__name__)

app.register_blueprint(Users_BP)
app.register_blueprint(Posts_BP)
app.register_blueprint(System_BP)




app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Begin 001.@localhost/our_users'

#Secret Key!
app.config['SECRET_KEY'] = "my super secret key"



#Upload image
UPLOAD_FOLDER = "static/images/"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#Iniciar Extensões
db.init_app(app)
migrate.init_app(app, db)
ckeditor.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'Users_BP.login'
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))