from flask_sqlalchemy import SQLAlchemy;
from flask_migrate import Migrate;
from flask_ckeditor import CKEditor;


db = SQLAlchemy()

migrate = Migrate()

ckeditor = CKEditor()

