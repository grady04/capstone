from logging import handlers
from app import db, login
from flask_login import UserMixin
from datetime import datetime as dt, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id')),
)

class Ranch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    # hands = db.relationship('Hand', backref='ranch', lazy="dynamic")

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name =  db.Column(db.String)
    email =  db.Column(db.String, unique=True, index=True)
    password =  db.Column(db.String)
    created_on = db.Column(db.DateTime, default=dt.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    tasks = db.relationship('Task', backref='author', lazy="dynamic")
    comments = db.relationship('Comments', backref='author', lazy="dynamic")
    #ranch_id = db.Column(db.Integer, db.ForeignKey('ranch_id'))
    ranch_name = db.Column(db.String)
    token = db.Column(db.String, index=True, unique=True)
    token_exp = db.Column(db.DateTime)
    followed = db.relationship('User',
        secondary = followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id ==id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy ='dynamic'
        )

    ##################################################
    ############## Methods for Token auth ############
    ##################################################
    def get_token(self, exp=86400):
        current_time = dt.utcnow()
        # give the user their back token if their is still valid
        if self.token and self.token_exp > current_time + timedelta(seconds=60):
            return self.token
        # if the token DNE or is exp
        self.token = secrets.token_urlsafe(32)
        self.token_exp = current_time + timedelta(seconds=exp)
        self.save()
        return self.token

    def revoke_token(self):
        self.token_exp = dt.utcnow() - timedelta(seconds=61)
    
    @staticmethod
    def check_token(token):
        u  = User.query.filter_by(token=token).first()
        if not u or u.token_exp < dt.utcnow():
            return None
        return u


    #########################################
    ############# End Methods for tokens ####
    #########################################

    def __repr__(self):
        return f'<User: {self.email} | {self.id}>'

    def __str__(self):
        return f'<User: {self.email} | {self.first_name} {self.last_name}>'

    def hash_password(self, original_password):
        return generate_password_hash(original_password)

    def check_hashed_password(self, login_password):
        return check_password_hash(self.password, login_password)

    def from_dict(self, data):
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email=data['email']
        self.ranch_name = data['ranch_name']
        self.password = self.hash_password(data['password'])

    def save(self):
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        return {
            'id':self.id,
            'first_name':self.first_name,
            'last_name':self.last_name,
            'email':self.email,
            'created_on':self.created_on,
            'is_admin':self.is_admin,
            'token':self.token
        }

    def ranch_tasks(self): # just like followed_posts in class
        #tasks = Task.query.join(followers, (Task.user_id == followers.c.followed_id)).filter(followers.c.follower_id == self.id)
        self_tasks = Task.query.filter_by(user_id = self.id)
        #all_tasks = tasks.union(self_tasks).order_by(Task.date_created.desc())
        return self_tasks

    def daily_tasks(self):
        self_tasks = Task.query.filter_by(user_id = self.id, daily=True)
        return self_tasks


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
    # SELECT * FROM user WHERE id = ???

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    date_created=db.Column(db.DateTime, default=dt.utcnow)
    date_updated=db.Column(db.DateTime, onupdate=dt.utcnow)
    urgent = db.Column(db.Boolean)
    daily = db.Column(db.Boolean)
    completed = db.Column(db.Boolean)
    comments = db.relationship('Comments', backref='job', lazy="dynamic")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def edit(self, new_body):
        self.body=new_body

    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        return {
            'id':self.id,
            'body':self.body,
            'date_created':self.date_created,
            'date_updated':self.date_updated,
            'urgent':self.urgent,
            'daily':self.daily,
            'comments':self.comments,
            'user_id':self.user_id,
            'author':self.author.first_name +' '+ self.author.last_name
        }
    
    def complete(self):
        self.complete = True
        

class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    date_created=db.Column(db.DateTime, default=dt.utcnow)
    text = db.Column(db.Text)

    def edit_comment(self, new_comment):
        self.text = new_comment

    def save(self):
        db.session.add(self)
        db.session.commit()

    def del_comment(self):
        db.session.delete(self)
        db.session.commit()