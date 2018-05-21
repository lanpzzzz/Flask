#!usr/bin/env python 
# -*- coding:utf-8 -*-
from . import db
from flask_login import UserMixin   #为了使用flask-Login扩展，以记录登录状态，需要使用UserMixin类默认实现一些方法，只需要导入这个类即可
from . import login_manager
from werkzeug.security import generate_password_hash,check_password_hash


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64),unique=True,index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User %r>' % self.username

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @property    #表示密码为空，不可读
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

#flask-login需要程序实现一个回调函数，根据不同标识符加载用户信息,是用来，当用户有保存过信息时自动写入用户信息的吗？
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))    


    def __repr__(self):
        return '<User %r>' % self.username