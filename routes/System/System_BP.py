
from pkgutil import extend_path
from flask import render_template, Blueprint

System_BP = Blueprint("System_BP", __name__, template_folder="templates")


#create a route decorator
@System_BP.route('/')
def index():
    first_name = "John"
    return render_template("index.html", first_name=first_name) 

# Invalid URL
@System_BP.errorhandler(404)
def page_not_found(e):
   return render_template("404.html"), 404  

# Internal Server Error
@System_BP.errorhandler(500)
def page_not_found(e):
   return render_template("500.html"), 500  

