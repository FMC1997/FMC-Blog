from flask_sqlalchemy import SQLAlchemy;
from flask_migrate import Migrate;
from flask_ckeditor import CKEditor;
import logging

logging.basicConfig(filename='record.log', level=logging.DEBUG)

db = SQLAlchemy()

    


migrate = Migrate()

ckeditor = CKEditor()

