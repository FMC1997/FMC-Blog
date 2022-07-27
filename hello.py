from flask import Flask, redirect, render_template, flash, request, url_for
from flask_wtf import FlaskForm;
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError;
from wtforms.validators import DataRequired, EqualTo, Length;
from datetime import datetime;
from flask_sqlalchemy import SQLAlchemy;
from flask_migrate import Migrate;
from werkzeug.security import generate_password_hash, check_password_hash;
from wtforms.widgets import TextArea

#create a Flask Instance
app = Flask(__name__)

#add Database SQLlite
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

#Add Database mySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Begin 001.@localhost/our_users'

#Secret Key!
app.config['SECRET_KEY'] = "my super secret key"

#Initialize The Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#Create a Blog Post Model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))

#Create a Posts Form 
class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    author = StringField("Author", validators=[DataRequired()])
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Submit", validators=[DataRequired()])

#Deleted a Post
@app.route('/posts/delete/<int:id>')
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
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
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data
        #Update post database
        db.session.add(post)
        db.session.commit()
        flash("Post Has been updated!")
        return redirect(url_for('post', id=post.id))
    form.title.data = post.title
    form.author.data = post.author
    form.slug.data = post.slug
    form.content.data = post.content
    return render_template('edit_post.html', form=form)

#Add Post Page
@app.route('/add-post', methods=['GET', 'Post'])
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        post = Posts(title = form.title.data,
                     content = form.content.data, 
                     author = form.author.data,
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



#Create Model
class Users(db.Model):
    id = db.Column (db.Integer, primary_key=True)
    name = db.Column (db.String(100), nullable=False)
    email = db.Column (db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    date_added = db.Column (db.DateTime, default=datetime.utcnow)
    #hashing password
    password_hash = db.Column(db.String(128));
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

@app.route('/delete/<int:id>')
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



#Create a User Form
class UserForm(FlaskForm):
    name = StringField("Name:", validators=[DataRequired()])
    email = StringField("Email:", validators=[DataRequired()])
    favorite_color = StringField("Favorite Color")
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Password Must Match!')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField("Submit")

# Update Database Record
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UserForm()
    name_to_update= Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        try:
            db.session.commit()
            flash("User Updated Sucessfully")
            return render_template("update.html",
            form=form,
            name_to_update = name_to_update)
        except:
            flash("Error! Looks like was a problem, try again!")
            return render_template("update.html",
            form=form,
            name_to_update = name_to_update)
    else:
        return render_template("update.html",
            form=form,
            name_to_update = name_to_update,
            id = id)


class PasswordForm(FlaskForm):
    email = StringField("What´s your Email", validators=[DataRequired()])
    password_hash = PasswordField("What´s your Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

#Create a Form Flask
class NamerForm(FlaskForm):
    name = StringField("What´s your name", validators=[DataRequired()])
    submit = SubmitField("Submit")

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
            user = Users(name=form.name.data, email=form.email.data, favorite_color=form.favorite_color.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
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

