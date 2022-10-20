
from importlib.metadata import packages_distributions
from flask import render_template, Blueprint, flash, redirect, url_for, request, current_app
from flask_login import login_required, current_user, login_user, logout_user
import os
from routes.Comments.Comments_BP import Comments
from routes.Posts.Posts_BP import Posts
from routes.Users.Users_BP import Users
from webforms import AddImage, PermissaoForm
from extensions import db

System_BP = Blueprint("System_BP", __name__,
                      template_folder="templates", static_folder="static")


# Rota para a página inicial
@System_BP.route('/')
def index():
    first_name = "John"
    page_title = "Pagina Inicial"
    return render_template("index.html", first_name=first_name, page_title=page_title)


# Rota para painel de adminstração
@System_BP.route('/admin')
# Verifica se o utilizador está login, se não manda para a página de login
@login_required
def admin():
    # Pega o current_user
    user = current_user.user_type
    # Se tiver permissoes de root abre a página
    if user == 1:
        page_title = "Admin Painel"
        return render_template("admin.html", page_title=page_title)
    else:
        flash("Não tens as permissões necessárias para entrar nesta página!", "erro")
        return redirect(url_for('Users_BP.dashboard'))


# Verifica quais as pastas dentro de static/images
def getImgFolders():
    # O sistema vai para a pasta static/imagens
    os.chdir("static/images")
    # Dá a lista das pastas
    Folders = os.listdir()
    # Devolve a lista de pastas
    return Folders


# Rota para monstrar as imagens dentro da pasta selecionada no painel de adminstração
@System_BP.route('/admin/gallery/<string:folder>')
@login_required  # Verifica se o utilizador está login, se não manda para a página de login
def gallery(folder):
    # Pega o current_user
    user = current_user.user_type
    # Se tiver permissoes de root abre a página
    if user == 1:
        # Para evitar erros de caminho, o sistema vai para a pasta root do projecto
        os.chdir(current_app.root_path)
        folders = getImgFolders()  # Pega as pastas de imagens, para depois mandar para o Modelo
        os.chdir(folder)  # Vai para a pasta de imagens selecionada
        imagens = os.listdir()  # Lista as imagens na pasta selecionada
        return render_template("gallery.html", imagens=imagens, folder=folder, folders=folders)
    else:
        # Se Não tiver permissoes manda para a página dashBoard
        flash("Não tens as permissões necessárias para entrar nesta página!", "erro")
        return redirect('/dashboard')


# Apaga a imagem selecionada pelo utilizador
@System_BP.route('/admin/removeImg/<string:img>')
@login_required
def removeImg(img):
    user = current_user.user_type
    if user == 1:
        os.remove(img)  # Apaga a imagem selecionada
        # Para evitar erros de caminho, o sistema vai para a pasta root do projecto
        os.chdir(current_app.root_path)
        return redirect(url_for('System_BP.gallery', folder='Posts'))
    else:
        # Se Não tiver permissoes manda para a página dashBoard
        flash("Não tens as permissões necessárias para entrar nesta página!", "erro")
        return redirect('/dashboard')


# Permite adcionar uma imagem na galeria
@System_BP.route('/admin/add_img')
@login_required
def addImg():
    user = current_user.user_type
    if user == 1:
        form = AddImage()  # set Form
        img_upload = form.request.files['img_upload']
        os.path.join("static/images/", img_upload)
        os.chdir(current_app.root_path)
        flash("Imagem guardada com sucesso!", "sucesso")
        return redirect(url_for('System_BP.gallery', folder='Posts'))
    else:
        # Se Não tiver permissoes manda para a página dashBoard
        flash("Não tens as permissões necessárias para entrar nesta página!", "erro")
        return redirect('/dashboard')


@System_BP.route('/admin/posts')
@login_required
def AdminPosts():
    user = current_user.user_type
    if user == 1:
        page_title = "Admin/Posts"
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("AdminPosts.html", id=current_user.id, posts=posts, page_title=page_title)
    else:
        # Se Não tiver permissoes manda para a página dashBoard
        flash("Não tens as permissões necessárias para entrar nesta página!", "erro")
        return redirect('/dashboard')


# Route para listar todos os utlizadores, para permitir apagar ou mudar permissões
@System_BP.route('/admin/users')
@login_required
def AdminUsers():
    user = current_user.user_type
    if user == 1:
        PermissaoF = PermissaoForm()  # set Form para mudar as permissoes
        users = Users.query.order_by(Users.id)
        page_title = "Admin/users"  # Dá a página um modelo
        return render_template("AdminUsers.html", id=current_user, users=users, page_title=page_title, form=PermissaoF)
    else:
        # Se Não tiver permissoes manda para a página dashBoard
        flash("Não tens as permissões necessárias para entrar nesta página!", "erro")
        return redirect('/dashboard')


@System_BP.route('/admin/setPermissao/<int:id>',  methods=['GET', 'POST'])
@login_required
def setPermissao(id):
    user = current_user.user_type
    if user == 1:
        user = Users.query.get_or_404(id)
        user.user_type = request.form['permissao']
        try:
            db.session.commit()
            flash("Utilizador atualizado com sucesso!", "sucesso")
        except:
            flash("Não conseguimos atualizar esse utilizador, tente novamente!", "erro")
        return redirect('/admin/users')
    else:
        # Se Não tiver permissoes manda para a página dashBoard
        flash("Não tens as permissões necessárias para entrar nesta página!", "erro")
        return redirect('/admin/users')
