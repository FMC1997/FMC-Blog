from crypt import methods
from flask import Flask, redirect, render_template, flash, request, url_for

from datetime import datetime
import flask;

from flask_sqlalchemy import SQLAlchemy;
from flask_migrate import Migrate;
from werkzeug.security import generate_password_hash, check_password_hash;

from flask_login import LoginManager, UserMixin, login_user, login_manager, logout_user, login_required, current_user;

from webforms import LoginForm, PostForm , UserForm, PasswordForm, NamerForm, SearchForm
from flask_ckeditor import CKEditor;





#create a Flask Instance
app = Flask(__name__)

ckeditor = CKEditor(app)



#Add SQLlite 
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

#Add Database mySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Begin 001.@localhost/our_users'

#Secret Key!
app.config['SECRET_KEY'] = "my super secret key"

#Initialize The Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#Flask_Login 
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

#Pass stuff to navbar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

#Admin route
@app.route('/admin')
@login_required
def admin():
    id = current_user.id
    if (id == 11):
        return render_template("admin.html") 
    else:
        flash("Sorry you must be the Admin to access")
        return redirect(url_for('dashboard'))

#Create a Search Function
@app.route('/search', methods=["POST"])
def search():
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        post.searched = form.searched.data
        posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
        posts = posts.order_by(Posts.title).all()
        return render_template("search.html", form=form, searched = post.searched, posts = posts)

#Create Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            #Check password hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login Successfully!!")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong Password - Try Again!!")
        else:
            flash("Username doesnt exist! - Try Again!!! ")
    return render_template('login.html', form=form)

#Create Logout Page
@app.route('/logout',methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You Have Been Logged Out!")
    return redirect(url_for('login'))

#Create Dashboard Page
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    
    return render_template('dashboard.html')




#Deleted a Post
@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.poster.id:
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


@app.route('/posts')
def posts():
    #Grab all the post from the database
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template("posts.html", posts = posts)

@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post)


#Edit Post Page
@app.route('/post/edit/<int:id>', methods=['GET', 'POST'])
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
        return redirect(url_for('post', id=post.id))
    if current_user.id == post.poster_id:
        form.title.data = post.title
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template('edit_post.html', form=form)
    else:
        flash("You aren´t Authorized To Edit This Post")
        posts()

#Add Post Page
@app.route('/add-post', methods=['GET', 'Post'])
@login_required
def add_post():
    
    form = PostForm()

    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(title = form.title.data,
                     content = form.content.data, 
                     poster_id=poster,
                     slug=form.slug.data)

        form.title.data = ''
        form.content.data = ''
        form.author.data = ''
        form.slug.data = ''
        #Add post data do database
        db.session.add(post)
        db.session.commit()
        flash("Blog Post Submitted Successfully")
    return render_template("add_post.html", form=form)





@app.route('/delete/<int:id>')
@login_required
def delete(id):
    user_to_delete= Users.query.get_or_404(id)
    name = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Sucessefully")
        our_users = Users.query.order_by(Users.date_added)
        return render_template("add_user.html", form = form, name=name, our_users=our_users )
    except:
        flash("Whoops! There was a problem, try Again")
        return render_template("add_user.html", form = form, name=name, our_users=our_users )




# Update Database Record
@app.route('/update/<int:id>', methods=['GET', 'POST'])
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
        try:
            db.session.commit()
            flash("User Updated Sucessfully")
            return render_template("update.html",
            form=form,
            name_to_update = name_to_update, id=id)
        except:
            flash("Error! Looks like was a problem, try again!")
            return render_template("update.html",
            form=form,
            name_to_update = name_to_update, id=id)
    else:
        return render_template("update.html",
            form=form,
            name_to_update = name_to_update,
            id = id)

@app.route('/user/add', methods=['GET', 'POST'])
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
        flash("User Added Successfully")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html", form = form, name=name, our_users=our_users )



#create a route decorator
@app.route('/')
def index():
    first_name = "John"
    return render_template("index.html", first_name=first_name) 

@app.route('/user/<name>')


def user(name):
    return render_template("user.html", user_name=name) 

#Custom error pages

# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
   return render_template("404.html"), 404  

# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
   return render_template("500.html"), 500  

#Create Password Test Page

@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None

    form = PasswordForm()
    #Validate Form 
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        form.email.data = ''
        form.password_hash.data = ''
        pw_to_check = Users.query.filter_by(email=email).first()

        #Check hask password
        passed = check_password_hash(pw_to_check.password_hash, password)

    return render_template("teste_pwd.html",email = email, password = password, pw_to_check = pw_to_check, passed=passed, form=form)    





#Create Name Page

@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()
    #Validate Form 
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form Submitted Sucessfully!")
    return render_template("name.html",name = name, form=form)    

#Create a Blog Post Model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    #author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))
    #Foreign Key To Link Users (refer to primary key to user)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))


#Create Model
class Users(db.Model, UserMixin):
    id = db.Column (db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column (db.String(100), nullable=False)
    email = db.Column (db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    about_author = db.Column(db.Text(500), nullable=True)
    date_added = db.Column (db.DateTime, default=datetime.utcnow)
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