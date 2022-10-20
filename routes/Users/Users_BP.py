
from flask import redirect, render_template, flash, request, Blueprint, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import uuid as uuid
import os
from flask_login import login_required, current_user, login_user, logout_user
from routes.Comments.Comments_BP import Comments
from routes.Posts.Posts_BP import Posts
from webforms import UserForm, LoginForm
from extensions import db
from flask_login import UserMixin
from datetime import datetime


# Definir pasta de modelos para o route
Users_BP = Blueprint("Users_BP", __name__, template_folder="Templates")


# Class para SQLAlchemy(ORM)
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    about_author = db.Column(db.Text(500), nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    profile_pic = db.Column(db.String(200), nullable=False)
    user_type = db.Column(db.Integer, nullable=False, default=3)

    # Palavra-passe
    password_hash = db.Column(db.String(128))

    # Ligação com as bases de dados dos Postes e comentários
    posts = db.relationship('Posts', backref='poster')
    comments = db.relationship('Comments', backref='Comments')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute!')

    # Codifica a palavra-passe
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # descodifica a palavra-passe e verifica se é igual ao que o utilizador digitou
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Criar String (Dá o erro FSADeprecationWarning)
    def __repr__(self):
        return '<Name %r>' % self.name


# Monstra informações de utilizadores
@Users_BP.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    page_title = "Dashboard"
    return render_template('dashboard.html', page_title=page_title)


# Apaga Utilizador
@Users_BP.route('/apagarUtilizador/<int:id>')
@login_required
def apagarUtilizador(id):
    # Verificar se o utilizador tem as permissoes necessárias, senão dá erro e volta para a dashBoard
    if id == current_user.id or current_user.user_type == 1:
        user_to_delete = Users.query.get_or_404(id)

        try:
            # Apagar imagem do user se existir
            if not (user_to_delete.profile_pic == "default"):
                os.chdir(current_app.root_path)
                caminhoIMG = 'static/images/Users/' + user_to_delete.profile_pic
                if os.path.exists(caminhoIMG):
                    os.remove(caminhoIMG)

            # Apagar Posts
            post_to_delete = Posts.query.filter_by(poster_id=id)
            for post in post_to_delete:
                caminhopost = 'static/images/Posts/' + post.post_pic
                if os.path.exists(caminhopost):
                    os.remove(caminhopost)
                db.session.delete(post)

            # Apagar comentários
            comments_to_delete = Comments.query.filter_by(user=id)
            for comment in comments_to_delete:
                db.session.delete(comment)

            # Apagar utilizador
            db.session.delete(user_to_delete)
            db.session.commit()

            # Sucesso
            flash("Utilizador apagado com sucesso!", "sucesso")
            return redirect('/Entrar')
        except:
            # Erro a apagar utilizador
            flash("Não conseguimos apagar esse utilizador, tente novamente!", "erro")

    else:
        flash("Não tens as permissões necessárias para apagar este utilizador!", "erro")
        return redirect('/dashboard')


# Atualizar Utilizador
@Users_BP.route('/atualizarUtilizador/<int:id>', methods=['GET', 'POST'])
@login_required
def atualizarUtilizador(id):

    # Verificar se o utilizador tem as permissoes necessárias, senão dá erro e volta para a dashBoard
    if id == current_user.id or current_user.user_type == 1:
        # Puxar Formulario
        form = UserForm()

        # Procura na base de dados o utilizador
        name_to_update = Users.query.get_or_404(id)
        page_title = "A atualizar o Utilizador " + name_to_update.username

        # Se o Utilizador terminar o formulário
        if request.method == "POST":

            # Se mudar a imagem de perfil
            if request.files['profile_pic']:
                # Pega a imagem anterior
                old_pic = name_to_update.profile_pic

                # Verificar se não é a imagem padrão
                if not (name_to_update.profile_pic == "default"):
                    # O sistema vai para a pasta da imagem
                    os.chdir(current_app.root_path + "/static/images/Users/")
                    # Verifica se existe a imagem(para evitar erros, a imagem pode ter sido apagada do sistema)
                    if os.path.exists(old_pic):
                        # Apaga finalmente a porra da imagem :) . Depois de experimentar vários cenários diferentes, para correr bem as coisas e evitar erros, é melhor verificar antes se existem...
                        os.remove(old_pic)

                # Agarra a imagem do formulário
                name_to_update.profile_pic = request.files['profile_pic']

                # Puxa a imagem em formato seguro (werkzeug.secure_filename)
                pic_filename = secure_filename(
                    name_to_update.profile_pic.filename)

                # Para evitar erros, substituição ou duplicação de imagem, as imagens vão ter um nome unico em uuid + nome da imagem
                pic_name = str(uuid.uuid1()) + "_" + pic_filename

                # Gravar a imagem no servidor
                name_to_update.profile_pic.save(os.path.join(pic_name))

                # Associar o nome na imagem na base de dados
                name_to_update.profile_pic = pic_name
            try:
                # Gera valores para base de dados
                name_to_update.name = form.name.data
                name_to_update.email = form.email.data
                name_to_update.about_author = form.about_author.data
                db.session.add(name_to_update)
                # Grava valores na base de dados
                db.session.commit()
                flash("Utilizador atualizado com sucesso!", "sucesso")
                return redirect('/dashboard')
            except:
                flash(
                    "Não foi possivel atualizar o utilizador, tente novamente!", "erro")

    else:
        flash(
            "Não tens as permissões necessárias para atualizar este utilizador!", "erro")
        return redirect('/dashboard')

    return render_template("update.html",
                           form=form,
                           name_to_update=name_to_update,
                           id=id, page_title=page_title)


# Route para registar novos utilizadores
@Users_BP.route('/user/Registo', methods=['GET', 'POST'])
def add_user():
    page_title = "Registo"
    form = UserForm()
    if form.validate_on_submit():
        # Verificar se esse Email é unico
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Verificar se o utilizador mudou a imagem de perfil
            if request.files['profile_pic']:
                try:
                    ImgFile = request.files['profile_pic']

                    # Puxa a imagem em formato seguro (werkzeug.secure_filename)
                    ImgFile_name = secure_filename(ImgFile.filename)
                    # Para evitar erros, substituição ou duplicação de imagem, as imagens vão ter um nome unico em uuid + nome da imagem
                    pic_name = str(uuid.uuid1()) + "_" + ImgFile_name

                    # Para evitar erros de caminho, o sistema vai para o caminho do projecto
                    os.chdir(current_app.root_path)
                    # Gravar a imagem
                    ImgFile.save(os.path.join("static/images/Users", pic_name))

                except:
                    flash(
                        "Não conseguimos colocar a imagem no nosso servidor, tente novamente!", "erro")
                    return render_template("add_user.html", form=form, name=name,  page_title=page_title)
            # Se o utilizador não mudou a imagem de perfil
            else:
                pic_name = "default"

            # Para proteger o utilizador a sua palavra-passe vai ser segura por sha256 (werkzeug.security)
            hashed_pw = generate_password_hash(
                form.password_hash.data, "sha256")

            # Pega tem todos os dados do formulário e coloca pendente na base de dados
            user = Users(username=form.username.data, name=form.name.data,
                         email=form.email.data, password_hash=hashed_pw, profile_pic=pic_name)
            db.session.add(user)

            # Gravar na base de dados
            db.session.commit()
        # Limpar campos do formulário
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.username = ''
        form.password_hash = ''
        flash("O seu utilizador foi criado com sucesso", "sucesso")
        return redirect('/Entrar')
    return render_template("add_user.html", form=form,  page_title=page_title)


# route para inicar sessão
@Users_BP.route('/Entrar', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    page_title = "Login"
    if form.validate_on_submit():
        # verifica se existe realmente o utilizador
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            # Descodifica e verifica a palavra-passe digitada
            if check_password_hash(user.password_hash, form.password.data):
                # Entrar em sessão
                login_user(user)

                flash("Entrada com sucesso!", "sucesso")
                return redirect('/Blog')
            else:
                flash("Palavra-passe incorreta!", "erro")
        else:
            flash("Utilizador não encontrado!", "erro")
    return render_template('login.html', form=form, page_title=page_title)


# Route para o utilizador sair de sessão
@Users_BP.route('/logout')
@login_required
def logout():
    # Sai da sessão
    logout_user()
    flash("Saida com sucesso!", "sucesso")
    return redirect('/Entrar')
