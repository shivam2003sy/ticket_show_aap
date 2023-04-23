# Python modules
import os, logging 
from datetime import datetime
# Flask modules
from flask  import render_template, request, url_for, redirect, send_from_directory , flash
from flask_login  import login_user, logout_user, current_user, login_required
from werkzeug.exceptions import HTTPException, NotFound, abort
from jinja2  import TemplateNotFound
# App modules
from app import app, lm, db, bc
from app.models import User , Venue , Show , Ticket
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
           shows = Show.query.join(Venue).filter(Venue.userid == user.id).all()
           return render_template('admin.html' , view = view , shows = shows)
        else:
             # query shows and their respective venues
            shows = db.session.query(Show, Venue).join(Venue).all()
            # pass the results to the template
            return render_template('index.html', shows=shows)
        
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
        # get venue id from url
        vid  = None
        if user.admin == True :
            if request.method == 'GET':
                id = int(request.args.get('id'))
                venue = Venue.query.filter_by(id = id).first()
                vid = venue.id
                return render_template('admin/createshow.html')
            else:
                # create show from model.py
                name  =  request.form.get('name', '', type=str)
                price =  request.form.get('price', '', type=int)
                starttime =  request.form.get('start-time', '', type=str)
                endtime =  request.form.get('end-time', '', type=str)
                date = request.form.get('date', '', type=str)
                tag = request.form.get('tag', '', type=str)
                rating = request.form.get('rating', '', type=int)
                #  handel time in sqlite endtime
                endtime  = datetime.strptime(endtime, '%H:%M')
                starttime = datetime.strptime(starttime, '%H:%M')
                # handel date in sqlite
                date = datetime.strptime(date, '%Y-%m-%d')
                show = Show(
                    name= name,
                    rating= rating,
                    ticketPrice= price,
                    startTime= starttime,
                    endTime= endtime,
                    date= date,
                    tags= tag,
                    venue_id=vid
                )

                show.save()
                return redirect(url_for('index'))
        else:
            return  render_template('index.html')
        

@app.route('/show/<int:id>', methods=['GET', 'POST'])
def show(id):
    # get show and venue by id
    show = Show.query.filter_by(id=id).first()
    venue = Venue.query.filter_by(id=show.venue_id).first()

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        num_tickets = int(request.form.get('num_tickets'))

        # check if there are enough available tickets
        if show.availability() < num_tickets:
            flash('Sorry, there are not enough tickets available', 'error')
        else:
            # create new ticket and add to database
            ticket = Ticket(show_id=show.id, user_id=current_user.id)
            db.session.add(ticket)
            db.session.commit()
            flash('Your tickets have been booked!', 'success')
            return redirect(url_for('show', id=id))

    # pass the results to the template
    return render_template('show.html', show=show, venue=venue)
