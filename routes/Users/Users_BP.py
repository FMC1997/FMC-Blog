from flask import redirect, render_template, flash, request, url_for,Blueprint
from werkzeug.security import generate_password_hash, check_password_hash;
from werkzeug.utils import secure_filename
import uuid as uuid
import os
from flask_login import login_required, current_user, login_user, logout_user
from webforms import UserForm, LoginForm
from extensions import db
from flask_login import  UserMixin
from datetime import datetime



Users_BP = Blueprint("Users_BP", __name__, static_folder="./static", template_folder="Templates")


@Users_BP.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    
    return render_template('dashboard.html')

@Users_BP.route('/delete/<int:id>')
@login_required
def delete(id):
    if id == current_user.id:
        user_to_delete= Users.query.get_or_404(id)
        name = None
        form = UserForm()
        try:
            db.session.delete(user_to_delete)
            db.session.commit()
            flash("Utilizador apagado com sucesso!", "sucesso")
            our_users = Users.query.order_by(Users.date_added)
            return render_template("Users/add_user.html", form = form, name=name, our_users=our_users )
        except:
            flash("Não conseguimos apagar esse utilizador, tente novamente!", "erro")
            return render_template("add_user.html", form = form, name=name, our_users=our_users )
    else:
        flash("Não tens as permissões necessárias para apagar este utilizador!", "erro")
        return redirect(url_for('dashboard'))


# Update Database Record
@Users_BP.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form = UserForm()
    name_to_update= Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.username = request.form['username']
        name_to_update.about_author = request.form['about_author']
        #check profile pic exist´s
        if request.files['profile_pic']:
            name_to_update.profile_pic = request.files['profile_pic']
            #Grap image in security system
            pic_filename = secure_filename(name_to_update.profile_pic.filename)
            #set uuid
            pic_name = str(uuid.uuid1()) + "_" + pic_filename
            #Save the image
            name_to_update.profile_pic.save(os.path.join("static/images/", pic_name))
            #Change to a string to save to db
            name_to_update.profile_pic = pic_name
            
            try:
                db.session.commit()
                flash("Utilizador atualizado com sucesso!", "sucesso")
                return render_template("dashboard.html",
                form=form,
                name_to_update = name_to_update, id=id)
            except:
                flash("Não conseguimos atualizar esse utilizador, tente novamente!", "erro")
                return render_template("update.html",
                form=form,
                name_to_update = name_to_update, id=id)
        else:
            db.session.commit()
            flash("Utilizador atualizado com sucesso!", "sucesso")
            return render_template("dashboard.html",
                form=form,
                name_to_update = name_to_update, id=id)

    else:
        return render_template("update.html",
            form=form,
            name_to_update = name_to_update,
            id = id)

@Users_BP.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        #Verificar se esse Email já está na base de dados
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            #Hash the password!!!
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(username = form.username.data, name=form.name.data, email=form.email.data, favorite_color=form.favorite_color.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.username = ''
        form.favorite_color.data = ''
        form.password_hash = ''
        flash("O seu utilizador foi criado com sucesso", "sucesso")
        return redirect(url_for('Users_BP.login'))
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html", form = form, name=name, our_users=our_users )



@Users_BP.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            #Check password hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Entrada com sucesso!", "sucesso")
                return redirect(url_for('Posts_BP.posts'))
            else:
                flash("Palavra-passe incorreta!", "erro")
        else:
            flash("Utilizador não encontrado!", "erro")
    return render_template('login.html', form=form)


#Create Logout Page
@Users_BP.route('/logout',methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("Saida com sucesso!", "sucesso")
    return redirect(url_for('Users_BP.login'))




class Users(db.Model, UserMixin):
    id = db.Column (db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column (db.String(100), nullable=False)
    email = db.Column (db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    about_author = db.Column(db.Text(500), nullable=True)
    date_added = db.Column (db.DateTime, default=datetime.utcnow)
    profile_pic = db.Column(db.String(200), nullable=True)
    #hashing password
    password_hash = db.Column(db.String(128));
    #User Can have many Posts
    posts = db.relationship('Posts', backref='poster')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password);
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password);

    #Create a String (Dá o erro FSADeprecationWarning)
    def __repr__(self):
        return '<Name %r>' % self.name



