from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import login_manager
from datetime import datetime


class Role(db.Model):
    __tablename__ = 'roles' 
    roleid = db.Column(db.Integer, primary_key = True)
    rolename = db.Column(db.String(40), unique = True)
    description = db.Column(db.Text)

    users = db.relationship('User', backref = 'role', lazy = 'dynamic')


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    userid = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(40), unique = True)
    roleid = db.Column(db.Integer, db.ForeignKey('roles.roleid'), default = 20)
    #description
    #userpic = db.Column()
    password_hash = db.Column(db.String(128))
    register_time = db.Column(db.DateTime, default = datetime.utcnow)
    #last_auth = db.Column(db.DateTime)
    email = db.Column(db.String(320), unique = True)
    addition = db.Column(db.Text)

    comments = db.relationship('Comment', backref = 'user', lazy = 'dynamic')
    stocks = db.relationship('StockSelection', backref = 'user', lazy = 'dynamic')

    @property
    def password(self):
        raise AttributeError('Password is not readable.')
    
    @property
    def id(self):
        return self.userid
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return '<USER {} {}>'.format(self.userid, self.username)
    

@login_manager.user_loader
def load_user(userid):
    return User.query.get(int(userid))


class Stock(db.Model):
    __tablename__ = 'stocks'
    stockid = db.Column(db.String(16), primary_key = True)
    stockname = db.Column(db.String(16))
    stocktype = db.Column(db.String(16))
    addition = db.Column(db.Text)

    selections = db.relationship('StockSelection', backref = 'stock', lazy = 'dynamic')
    closes = db.relationship('StockClose', backref = 'stock', lazy = 'dynamic')
    comments = db.relationship('Comment', backref = 'stock', lazy = 'dynamic')

    def __repr__(self):
        return '<STOCK> {} {}'.format(self.stockid, self.stockname)


class Comment(db.Model):
    __tablename__ = 'comments'
    commentid = db.Column(db.Integer, primary_key = True)
    comtime = db.Column(db.DateTime, default = datetime.utcnow)
    userid = db.Column(db.Integer, db.ForeignKey('users.userid'))
    stockid = db.Column(db.String(16), db.ForeignKey('stocks.stockid'))
    content = db.Column(db.Text)
    label = db.Column(db.Integer)
    status = db.Column(db.Boolean)
    reply = db.Column(db.Integer, db.ForeignKey('comments.commentid'))
    directreply = db.Column(db.Integer, db.ForeignKey('comments.commentid'))
    addtion = db.Column(db.Text)

    replyobject = db.relationship('Comment', foreign_keys = [reply], backref = 'replied', remote_side = [commentid])
    directreplyobject = db.relationship('Comment', foreign_keys = [directreply], backref = 'directreplied', remote_side = [commentid])


class StockClose(db.Model):
    __tablename__ = 'stockcloses'
    stockid = db.Column(db.String(16), db.ForeignKey('stocks.stockid'), primary_key = True)
    tradedate = db.Column(db.Date, primary_key = True)
    open = db.Column(db.Float)
    close = db.Column(db.Float)
    high = db.Column(db.Float)
    low = db.Column(db.Float)
    volume = db.Column(db.Integer)

    def json_data(self):
        return [self.tradedate.strftime('%Y-%m-%d'), self.open, self.close, self.high, self.low, self.volume]


class StockSelection(db.Model):
    __tablename__ = 'stockselections'
    userid = db.Column(db.Integer, db.ForeignKey('users.userid'), primary_key = True)
    stockid = db.Column(db.String(16), db.ForeignKey('stocks.stockid'), primary_key = True)
    addition = db.Column(db.Text)