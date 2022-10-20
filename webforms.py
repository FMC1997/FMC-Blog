from random import choices
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, EmailField, SelectField
from wtforms.validators import DataRequired, EqualTo, Length
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField


class AddImage(FlaskForm):
    img_upload = FileField("img_upload")


class SearchForm(FlaskForm):
    searched = StringField("Pesquisar: ", validators=[DataRequired()])
    submit = SubmitField("Pesquisar")


class LoginForm(FlaskForm):
    username = StringField("Utilizador:", validators=[DataRequired(), Length(
        min=3, max=20, message="Tem que conter entre 3 a 20 caracteres")])
    password = PasswordField("Palavra-passe:", validators=[DataRequired(), Length(
        min=7, max=20, message="Tem que conter entre 7 a 20 caracteres")])
    submit = SubmitField("Entrar!")


class PostForm(FlaskForm):
    title = StringField("Titulo:", validators=[DataRequired()])
    content = CKEditorField('Corpo:', validators=[DataRequired()])
    author = StringField("Autor:")
    slug = StringField("Titulo:", validators=[DataRequired()])
    post_pic = FileField("Imagem principal:")
    submit = SubmitField("Submeter::", validators=[DataRequired()])


class UserForm(FlaskForm):
    name = StringField("Nome:", validators=[DataRequired(), Length(
        min=3, max=20, message="Tem que conter entre 3 a 20 caracteres")])
    username = StringField("Utilizador:", validators=[DataRequired(), Length(
        min=3, max=20, message="Tem que conter entre 3 a 20 caracteres")])
    email = EmailField("Email:", validators=[DataRequired()])
    about_author = TextAreaField("Sobre mim:")
    password_hash = PasswordField('Palavra-passe: ', validators=[DataRequired(), EqualTo(
        'password_hash2', message='Password Must Match!'), Length(min=7, max=20, message="Tem que conter entre 7 a 20 caracteres")])
    password_hash2 = PasswordField(
        'Confirmar Palavra-passe:', validators=[DataRequired()])
    profile_pic = FileField("Imagem do Perfil")
    submit = SubmitField("Submeter")


class CommentForm(FlaskForm):
    comment = TextAreaField("Comentário", validators=[DataRequired(), Length(
        min=3, max=20, message="Tem que conter entre 3 a 20 caracteres")])
    submit = SubmitField("Submeter")


class PermissaoForm(FlaskForm):
    permissao = SelectField("permissao", choices=[(
        '1', '1- Root'), ('2', '2- Poster'), ('3', '3- User')])
    submit = SubmitField("Atualizar Permissão")
