from contextlib import nullcontext
from email.policy import default
from xml.etree.ElementTree import Comment
from flask import  redirect, render_template, flash, url_for, Blueprint, request
from datetime import datetime
from flask_login import current_user
from extensions import db
from webforms import CommentForm


Comments_BP = Blueprint("Comments_BP", __name__, static_folder="./static", template_folder="Templates")

class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    comment = db.Column(db.Text)
    post = db.Column(db.Integer, db.ForeignKey('posts.id'))
    user = db.Column(db.Integer, db.ForeignKey('users.id'))


def createComment(id):
    form = CommentForm()
    if request.method == "POST":
        Comment = Comments(comment= request.form["comment"],
                            post = id,
                            user= current_user )
    try:
        db.session.add(Comment)
        db.session.commit()
        form.comment.data = ""
    except:
        flash("Erro a publicar o seu commentário, tente novamente!", "erro")
    return render_template("createComment.html", form=form)

def showComments():
    comments = Comments.query.order_by(Comments.date)
    return render_template("showComments.html", comments=comments)

def deleteComment(id):
    CommentToDelete = Comments.query.get_or_404(id)
    id = current_user.id
    if id == CommentToDelete.user.id or id == 11:
        try:
            db.session.delete(CommentToDelete)
            db.session.commit()
            flash("O Post foi apagado com sucesso!", "sucesso")
        except:
             flash("Houve um problema a apagar o seu comentário, tente novamente mais tarde", "erro")
    return nullcontext

def editComment(id):
    CommentToEdit = Comments.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        CommentToEdit.comment = request.form["comment"]
        try:
            db.session.add(CommentToEdit)
            db.session.commit()
            flash("O seu comentário foi atualizado com sucesso!", "sucesso")
        except:
             flash("Houve um problema a editar o seu comentário, tente novamente mais tarde", "erro")
    return render_template("createComment.html", form=form)
