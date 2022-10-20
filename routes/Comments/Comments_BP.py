from asyncio.windows_events import NULL
from contextlib import nullcontext
from email.policy import default
from flask import redirect, render_template, flash, url_for, Blueprint, request
from datetime import datetime
from flask_login import current_user, login_required
from extensions import db
from webforms import CommentForm


Comments_BP = Blueprint("Comments_BP", __name__,
                        static_folder="./static", template_folder="Templates")

# Class para SQLAlchemy(ORM)


class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    comment = db.Column(db.Text)
    post = db.Column(db.Integer, db.ForeignKey('posts.id'))
    user = db.Column(db.Integer, db.ForeignKey('users.id'))


# Monstra todos os comentários do post
def showComments(id):
    comments = Comments.query
    comments = comments.filter(Comments.post.like(id), Comments.user != NULL)

    comments = comments.order_by(Comments.date)
    return comments


# Cria novo comentário
@Comments_BP.route('/newComment/<int:id>', methods=['GET', 'POST'])
@login_required
def newComment(id):
    formComment = CommentForm()
    page_title = "Adicionar Comentário"
    if request.method == "POST":
        user = current_user.id
        post = id
        Comment = Comments(post=post, user=user,
                           comment=request.form["comment"])
        try:
            db.session.add(Comment)
            db.session.commit()
            flash("O Comentário foi publicado com sucesso!", "sucesso")
        except:
            flash("Ocorreu a criar o seu post, tente novamente", "erro")
        return redirect(url_for('Posts_BP.post', id=id))

    return render_template("createComment.html", formComment=formComment, page_title=page_title)


# Editar o comentário
@Comments_BP.route('/editComment/<int:Commentid>/<int:postId>', methods=['GET', 'POST'])
@login_required
def editComment(Commentid, postId):
    formComment = CommentForm()
    commentdb = Comments.query.get_or_404(Commentid)

    if formComment.validate_on_submit():
        commentdb.comment = formComment.comment.data
        try:
            db.session.add(commentdb)
            db.session.commit()
            flash("O Comentário foi publicado com sucesso!", "sucesso")
            return redirect(url_for('Posts_BP.post', id=postId))
        except:
            flash("Erro na base de dados", "erro")
    if current_user.id == commentdb.user:
        page_title = "A editar Comentário"
        formComment.comment.data = commentdb.comment
        return render_template("createComment.html", formComment=formComment, page_title=page_title)
    else:
        flash("Não tens a permissões necessárias para editar este comentário!", "erro")
        return redirect(url_for('Posts_BP.post', id=postId))


# Apagar o comentário
@Comments_BP.route('/deleteComment/<int:Comment_id>/<int:postId>')
def deleteComment(Comment_id, postId):
    comment_to_delete = Comments.query.get_or_404(Comment_id)
    if current_user.id == comment_to_delete.user:
        try:
            db.session.delete(comment_to_delete)
            db.session.commit()
            flash("O Post foi apagado com sucesso!", "sucesso")
        except:
            flash("Ocorreu um erro a apagar o comentário, tente novamente", "erro")
        return redirect(url_for('Posts_BP.post', id=postId))
