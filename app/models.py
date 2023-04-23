from app import db
from flask_login import UserMixin



class User(UserMixin, db.Model):

    id = db.Column(db.Integer,     primary_key=True)
    user = db.Column(db.String(64),  unique = True)
    email = db.Column(db.String(120), unique = True)
    password = db.Column(db.String(500))
# admin fild
    admin = db.Column(db.Boolean, default=False)
    def __init__(self, user, email, password ,admin):
        self.user       = user
        self.password   = password
        self.email      = email
        self.admin      = admin

    def __repr__(self):
        return str(self.id) + ' - ' + str(self.user)

    def save(self):
        # inject self into db session    
        db.session.add ( self )
        # commit change and save the object
        db.session.commit()
        return self 
class Venue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64),  unique = True)
    place = db.Column(db.String(120), unique = True)
    capacity = db.Column(db.Integer)
    shows = db.relationship('Show', backref='venue')
    userid = db.Column(db.Integer, db.ForeignKey('user.id'))
    def __init__(self, name, place, capacity , userid):
        self.name       = name
        self.place      = place
        self.capacity   = capacity
        self.userid     = userid

    def __repr__(self):
        return str(self.id) + ' - ' + str(self.name)

    def save(self):
        # inject self into db session    
        db.session.add ( self )
        # commit change and save the object
        db.session.commit()
        return self


class   Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64),  unique = True)
    rating = db.Column(db.Integer)
    tags = db.Column(db.String(500))
    ticketPrice = db.Column(db.Integer)
    startTime = db.Column(db.DateTime)
    endTime = db.Column(db.DateTime)
    date = db.Column(db.DateTime)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))
    def __init__(self, name, rating, tags, ticketPrice, venue_id , date, startTime, endTime):
        self.name       = name
        self.rating     = rating
        self.tags       = tags
        self.ticketPrice = ticketPrice
        self.venue_id   = venue_id
        self.date       = date
        self.startTime  = startTime
        self.endTime    = endTime

    def availability(self):
        c= self.venue.capacity
        if c : 
            return int(c) - (len(self.tickets))

    def __repr__(self):
        return str(self.id) + ' - ' + str(self.name)

    def save(self):
        # inject self into db session    
        db.session.add ( self )
        # commit change and save the object
        db.session.commit()
        return self

class   Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    show = db.relationship('Show', backref='tickets')
    user = db.relationship('User', backref='tickets')

    def __init__(self, show_id, user_id):
        self.show_id    = show_id
        self.user_id    = user_id

    def __repr__(self):
        return str(self.id) + ' - ' + str(self.show_id) + ' - ' + str(self.user_id)

    def save(self):
        # inject self into db session    
        db.session.add ( self )
        # commit change and save the object
        db.session.commit()
        return self



