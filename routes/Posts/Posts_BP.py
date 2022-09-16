from flask import  redirect, render_template, flash, url_for, Blueprint, request
from datetime import datetime
from webforms import PostForm, SearchForm
from flask_login import login_required, current_user;
from extensions import db
import os
from werkzeug.utils import secure_filename


Posts_BP = Blueprint("Posts_BP", __name__, static_folder="./static", template_folder="Templates")

class Posts(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            title = db.Column(db.String(255))
            content = db.Column(db.Text)
            #author = db.Column(db.String(255))
            date_posted = db.Column(db.DateTime, default=datetime.utcnow)
            slug = db.Column(db.String(255))
            post_pic = db.Column(db.String(200), nullable=False)
            #Foreign Key To Link Users (refer to primary key to user)
            poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))

#Deleted a Post
@Posts_BP.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.poster.id or id == 11:
        try:
            db.session.delete(post_to_delete)
            db.session.commit()
            #return a message
            flash("O Post foi apagado com sucesso!", "sucesso")
            return redirect('/posts')
                
        except:
            flash("Houve um problema a apagar o seu Post, tente novamente mais tarde", "erro")
            return redirect('/posts')
    else:
        flash("Não tens a permissões necessárias para apagar este post", "erro")
        return redirect('/posts')


@Posts_BP.route('/posts')
def posts():
    page_title = "Blog"
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template("posts.html", posts = posts, page_title=page_title)

@Posts_BP.route('/post/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    page_title = post.title 
    return render_template('post.html', post=post, page_title=page_title)


#Edit Post Page
@Posts_BP.route('/post/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.slug = form.slug.data
        post.content = form.content.data
        #Update post database
        db.session.add(post)
        db.session.commit()
        flash("O Post foi atualizado com sucesso!", "sucesso")
        page_title = post.title 
        return redirect('/posts')
    if current_user.id == post.poster_id:
        page_title = 'A editar "' + post.title + '"' 
        form.title.data = post.title
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template("add_post.html", form=form, page_title=page_title)
    else:
        flash("Não tens a permissões necessárias para apagar este post!", "erro")
        return redirect('/posts')

#Add Post Page
@Posts_BP.route('/add-post', methods=['POST', 'GET'])
@login_required
def add_post():
    form = PostForm()
    page_title = 'A escrever um novo post' 
    
    if request.method == "POST":
        poster = current_user.id
        post = Posts(title = request.form["title"],
                        content = request.form["content"],
                        poster_id=poster,
                        slug=request.form["slug"])
        if request.files['post_pic']:
            post.post_pic = request.files['post_pic']    
            pic_filename = secure_filename(post.post_pic.filename)         
            post.post_pic.save(os.path.join("static/images/", pic_filename))
            post.post_pic = pic_filename
        try:
            db.session.add(post)
            db.session.commit()
            form.title.data = ''
            form.content.data = ''
            form.author.data = ''
            form.slug.data = ''
            form.post_pic.data = ''
            flash("O Post foi publicado com sucesso!", "sucesso")
            return redirect('/posts')
        
        except:
            flash("Erro a publicar o seu post, tente novamente!", "erro")
            return render_template("add_post.html", form=form, page_title=page_title)
        
        else:
            flash("Erro a gravar a sua imagem, tente novamente!", "erro")
            return render_template("add_post.html", form=form, page_title=page_title)
    return render_template("add_post.html", form=form, page_title=page_title)


#Create a Search Function
@Posts_BP.route('/search', methods=["POST"])
def search():
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        searched = form.searched.data
        posts = posts.filter(Posts.content.like('%' + searched + '%'))
        posts = posts.order_by(Posts.title).all()
        return redirect('/posts')
    else:
        flash("Não foi encontrado nenhum post com a palavra '" + form.searched.data +"'!", "erro" )
    return redirect('/posts')

@Posts_BP.context_processor
def base():
    form = SearchForm()
    return dict(form=form)