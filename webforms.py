from flask_wtf import FlaskForm;
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError;
from wtforms.validators import DataRequired, EqualTo, Length;
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField




class SearchForm(FlaskForm):
    searched = StringField("Searched", validators=[DataRequired()])
    submit = SubmitField("Submit")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")



class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    #content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    content = CKEditorField('Content', validators=[DataRequired()])
    author = StringField("Author")
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Submit", validators=[DataRequired()])



class UserForm(FlaskForm):
    name = StringField("Name:", validators=[DataRequired()])
    username =StringField("Username:", validators=[DataRequired()])
    email = StringField("Email:", validators=[DataRequired()])
    favorite_color = StringField("Favorite Color")
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Password Must Match!')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField("Submit")



class PasswordForm(FlaskForm):
    email = StringField("What´s your Email", validators=[DataRequired()])
    password_hash = PasswordField("What´s your Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

#Create a Form Flask
class NamerForm(FlaskForm):
    name = StringField("What´s your name", validators=[DataRequired()])
    submit = SubmitField("Submit")