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
            flash("Post Was Deleted!")
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts = posts)
                
        except:
            flash("Whooops! There was a problem deleting post, try again...")
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts = posts)
    else:
        flash("You aren´t Authorized To Delete That Post!!")
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts = posts)


@Posts_BP.route('/posts')
def posts():
    #Grab all the post from the database
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template("posts.html", posts = posts)

@Posts_BP.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post)


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
        flash("Post Has been updated!")
        return render_template('post.html', post=post)
    if current_user.id == post.poster_id:
        page_title = 'A editar "' + post.title + '"' 
        form.title.data = post.title
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template("add_post.html", form=form, page_title=page_title)
    else:
        flash("You aren´t Authorized To Edit This Post")
        posts()

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
            flash("Blog Post Submitted Successfully")
            
            return render_template("add_post.html", form=form, page_title=page_title)
        
        except:
            flash("Erro a publicar o seu post, tente novamente")
            return render_template("add_post.html", form=form, page_title=page_title)
        
        else:
            flash("Erro a puxar a imagem")
            return render_template("add_post.html", form=form, page_title=page_title)
    return render_template("add_post.html", form=form, page_title=page_title)


#Create a Search Function
@Posts_BP.route('/search', methods=["POST"])
def search():
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        post.searched = form.searched.data
        posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
        posts = posts.order_by(Posts.title).all()
        return render_template("search.html", form=form, searched = post.searched, posts = posts)
    else:
        flash("Search empthy!")
        return render_template("posts.html", posts = posts)