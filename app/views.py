# Python modules
import os, logging 

# Flask modules
from flask  import render_template, request, url_for, redirect, send_from_directory
from flask_login  import login_user, logout_user, current_user, login_required
from werkzeug.exceptions import HTTPException, NotFound, abort
from jinja2  import TemplateNotFound

# App modules
from app import app, lm, db, bc
from app.models import User , Venue , Show
from app.forms import LoginForm, RegisterForm

# provide login manager with load_user callback
@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Logout user
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# Register a new user
@app.route('/register', methods=['GET', 'POST'])
def register():
    # declare the Registration Form
    form = RegisterForm(request.form)
    msg     = None
    success = False
    if request.method == 'GET': 
        return render_template( 'accounts/register.html', form=form, msg=msg )
    # check if both http method is POST and form is valid on submit
# get  data from html form
    try:
        if (request.form['admin']):
            admin = True
        else:
            admin = False
    except:
        admin = False

    if form.validate_on_submit():
        # assign form data to variables
        username = request.form.get('username', '', type=str)
        password = request.form.get('password', '', type=str) 
        email    = request.form.get('email'   , '', type=str) 
        # filter User out of database through username
        user = User.query.filter_by(user=username).first()
        # filter User out of database through username
        user_by_email = User.query.filter_by(email=email).first()
        if user or user_by_email:
            msg = 'Error: User exists!'
        else:         
            pw_hash = password
            user = User(username, email, pw_hash , admin)
            user.save()
            msg = 'User created, please <a href="' + url_for('login') + '">login</a>'     
            success = True
    else:
        msg = 'Input error'     
    return render_template( 'accounts/register.html', form=form, msg=msg, success=success )
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Declare the login form
    form = LoginForm(request.form)
    # Flask message injected into the page, in case of any errors
    msg = None
    # check if both http method is POST and form is valid on submit
    try : 
        if (request.form['admin']):
            admin = True
        else:
            admin = False
    except:
        admin = False
    if form.validate_on_submit():
        # assign form data to variables
        username = request.form.get('username', '', type=str)
        password = request.form.get('password', '', type=str) 
        # filter User out of database through username
        user = User.query.filter_by(user=username).first()
        if user:
            if  password  == user.password:
                login_user(user)
                return redirect(url_for('index'))
            else:
                msg = "Wrong password. Please try again."
        else:
            msg = "No user registerd with this usename " 
    return render_template( 'accounts/login.html', form=form, msg=msg )

@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    else:
        user = User.query.filter_by(user=current_user.user).first()
        if user.admin == True :
           view = Venue.query.filter_by(userid = user.id).all()
           return render_template('admin.html' , view = view)
        else:
            return  render_template('index.html')
        
@app.route('/createvenue' , methods=['GET', 'POST'])
def createvenue():
    if not current_user.is_authenticated : 
        return redirect(url_for('login'))
    else:
        user = User.query.filter_by(user=current_user.user).first()
        if user.admin == True :
            if request.method == 'GET':
                return render_template('admin/CreateVenue.html')
            else:
                name = request.form.get('name', '', type=str)
                address = request.form.get('address', '', type=str)
                capacity = request.form.get('Capacity', '', type=int)
                venue = Venue(name, address, capacity  , user.id)
                venue.save()
                return redirect(url_for('index'))
        else:
            return  render_template('index.html')
@app.route('/createshow' , methods=['GET', 'POST'])
def create_show():
    if not current_user.is_authenticated : 
        return redirect(url_for('login'))
    else:
        user = User.query.filter_by(user=current_user.user).first()
        if user.admin == True :
            return render_template('admin/createshow.html')
        else:
            return  render_template('index.html')