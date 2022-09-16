
from flask import render_template, Blueprint, flash, redirect, url_for, request
from flask_login import login_required, current_user, login_user, logout_user
import os
from routes.Posts.Posts_BP import Posts_BP
from webforms import SearchForm
from webforms import AddImage

System_BP = Blueprint("System_BP", __name__, template_folder="templates", static_folder="static")


#create a route decorator
@System_BP.route('/')
def index():
    first_name = "John"
    page_title = "Pagina Inicial"
    return render_template("index.html", first_name=first_name, page_title=page_title) 

# Invalid URL
@System_BP.errorhandler(404)
def page_not_found(e):
   return render_template("404.html"), 404  

# Internal Server Error
@System_BP.errorhandler(500)
def page_not_found(e):
   return render_template("500.html"), 500  


#Admin route
@System_BP.route('/admin')
@login_required
def admin():
    page_title = "Admin Painel"
    id = current_user.id
    if (id == 3):
        return render_template("admin.html", page_title=page_title) 
    else:
        flash("Não tens as permissões necessárias para entrar nesta página!", "erro")
        return redirect(url_for('dashboard'))





#Admin route
@System_BP.route('/admin/gallery')
@login_required
def gallery():
    page_title = "Galeria de Imagens"
    id = current_user.id
    if (id == 3):
        caminho = "/home/fmc/Work_Space/flasker"
        os.chdir("static/images/")
        imagens = os.listdir()
        
        os.chdir(caminho)
        return render_template("gallery.html", imagens=imagens,page_title=page_title) 
    else:
        flash("Não tens as permissões necessárias para entrar nesta página!", "erro")
        return redirect('/dashboard')


@System_BP.route('/admin/removeAll-img')
@login_required
def removeAll_img():
    id = current_user.id
    if (id == 3):
        caminho = "/home/fmc/Work_Space/flasker"
        os.chdir("static/images/")
        imagens = os.listdir()
        for img in imagens:
            os.remove(img)
        os.chdir(caminho)
        return redirect('/admin/gallery')
    else:
        return redirect('/dashboard')

@System_BP.route('/admin/add_img')
@login_required
def addImg():
    id = current_user.id
    if (id == 3):
        form = AddImage()
        img_upload = form.request.files['img_upload']
        caminho = "/home/fmc/Work_Space/flasker"
        os.path.join("static/images/", img_upload)
        os.chdir(caminho)
        flash("Imagem guardada com sucesso!", "sucesso")
        return redirect('/admin/gallery')
    else:
        flash("Não tens as permissões necessárias para entrar nesta página!", "erro")
        return redirect('/dashboard')
    






