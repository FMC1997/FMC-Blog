from flask import redirect, render_template, flash, Blueprint, request, current_app
from datetime import datetime
from routes.Comments.Comments_BP import showComments
from webforms import PostForm, SearchForm
from flask_login import login_required, current_user
from extensions import db
import os
from werkzeug.utils import secure_filename


# Definir pasta de modelos para o route
Posts_BP = Blueprint("Posts_BP", __name__, template_folder="Templates")


# Class para SQLAlchemy(ORM)
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))
    post_pic = db.Column(db.String(200), nullable=False)
    # Associar bases de dados
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comments', backref='comments')


# Monstra todos os posts
@Posts_BP.route('/Blog')
def Blog():
    page_title = "Blog"
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template("posts.html", posts=posts, page_title=page_title)


# Apaga o Post Selecionado
@Posts_BP.route('/Blog/delete/<int:id>')
# Necessida de utilizador
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    # Verificar Permissoes
    if current_user.id == post_to_delete.poster_id or current_user.user_type == 1:
        try:

            # Vai para o caminho root
            os.chdir(current_app.root_path + '/static/images/Posts/')

            # Verifica se a imagem existe
            if os.path.exists(post_to_delete.post_pic):
                # Apaga imagem
                os.remove(post_to_delete.post_pic)

            # Apaga na base de dados o post
            db.session.delete(post_to_delete)
            db.session.commit()
            # Sucesso
            flash("O Post foi apagado com sucesso!", "sucesso")
            return redirect('/Blog')
        except:  # erro
            flash("Ocorreu um erro a apagar o Post, tente novamente", "erro")
    # erro de permissoes
    else:
        flash("Não tens permissoes para apagar este post", "erro")
        return redirect('/Blog')


# Monstra página de post
@Posts_BP.route('/post/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    page_title = post.title
    Comments = showComments(post.id)
    return render_template('post.html', post=post, page_title=page_title, Comments=Comments)


# Editar Post
@Posts_BP.route('/post/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    # Pega na base de dados o Post
    post_to_edit = Posts.query.get_or_404(id)
    if current_user.id == post_to_edit.poster_id or current_user.user_type == 1:
        page_title = 'A editar "' + post_to_edit.title + '"'

        # Puxa Form
        form = PostForm()
        # Coloca os valores da base de dados no Formulário
        form.title.data = post_to_edit.title
        form.slug.data = post_to_edit.slug
        form.content.data = post_to_edit.content

        # Ao Terminar o Formulário
        if request.method == "POST":
            if request.files['post_pic']:
                # Pega na imagem
                newIMG = request.files['post_pic']

                # Puxa a imagem em formato seguro (werkzeug.secure_filename)
                pic_filename = secure_filename(newIMG.filename)

                # O sistema vai para a pasta da imagem
                os.chdir(current_app.root_path + "/static/images/Posts")

                # Grava a imagem no servidor
                newIMG.save(os.path.join(pic_filename))
                post_to_edit.post_pic = pic_filename
            try:
                # Pega nos dados do Formulário e mete na base de dados
                post_to_edit.title = request.form["title"]
                post_to_edit.slug = request.form["slug"]
                post_to_edit.content = request.form["content"]
                # Grava na base de dados
                db.session.add(post_to_edit)
                db.session.commit()
                # Sucesso
                flash("O Post foi atualizado com sucesso!", "sucesso")
                return redirect('/Blog')
            # Erro a publicar
            except:
                flash("Não foi possivel editar este post!, tente novamente", "erro")

    # Erro de permissões
    else:
        flash("Não tens a permissões necessárias para editar este post!", "erro")
        return redirect('/Blog')

    return render_template("add_post.html", form=form, page_title=page_title)

# Route para criar Post


@Posts_BP.route('/add-post', methods=['POST', 'GET'])
@login_required
def add_post():
    # Verifica permissoes
    if current_user.user_type == 1 or current_user.user_type == 2:
        # Puxa Formulário
        form = PostForm()
        page_title = 'Escrever um novo post'

        if request.method == "POST":
            # Define qual o Poster
            poster = current_user.id

            # Se o utilizador mudar a imagem
            if request.files['post_pic']:
                # Pega na imagem
                newIMG = request.files['post_pic']

                # Puxa a imagem em formato seguro (werkzeug.secure_filename)
                pic_filename = secure_filename(newIMG.filename)

                # O sistema vai para a pasta da imagem
                os.chdir(current_app.root_path + "/static/images/Posts")

                # Grava a imagem no servidor
                newIMG.save(os.path.join(pic_filename))

                # Grava agora em formato seguro

            else:
                flash("Erro a gravar a sua imagem, tente novamente!", "erro")
                return render_template("add_post.html", form=form, page_title=page_title)

            # tenta gravar na base de dados e reseta os campos do formulário
            try:
                # Agarra os dados do form e adiciona na base de dados
                post = Posts(title=request.form["title"],
                             content=request.form["content"],
                             poster_id=poster,
                             slug=request.form["slug"], post_pic=pic_filename)
                db.session.add(post)
                db.session.commit()
                form.title.data = ''
                form.content.data = ''
                form.author.data = ''
                form.slug.data = ''
                form.post_pic.data = ''

                # Sucesso
                flash("O Post foi publicado com sucesso!", "sucesso")
                return redirect('/Blog')

            # Erro a publicar Post
            except:
                flash("Erro a publicar o seu post, tente novamente!", "erro")
                return render_template("add_post.html", form=form, page_title=page_title)
        #
        return render_template("add_post.html", form=form, page_title=page_title)
    # erro de permissoes
    else:
        flash("Não tens a permissões necessárias para apagar este post!", "erro")
        return redirect('/Blog')


# Formulário de pesquisa
@Posts_BP.route('/search', methods=["POST"])
def search():
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        searched = form.searched.data
        posts = posts.filter(Posts.content.like('%' + searched + '%'))
        posts = posts.order_by(Posts.title).all()
        return redirect('/Blog')
    else:
        flash("Não foi encontrado nenhum post com a palavra '" +
              form.searched.data + "'!", "erro")
    return redirect('/Blog')


@Posts_BP.context_processor
def base():
    form = SearchForm()
    return dict(form=form)
