#!usr/bin/env python 
# -*- coding:utf-8 -*-
from . import db
from flask_login import UserMixin,AnonymousUserMixin   #为了使用flask-Login扩展，以记录登录状态，需要使用UserMixin类默认实现一些方法，只需要导入这个类即可
from . import login_manager
from werkzeug.security import generate_password_hash,check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from datetime import datetime

class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')
###    
    ##增加默认属性，用户注册时，其角色被设为默认角色
    default = db.Column(db.Boolean, default=False, index=True)
    #permission字段，值是整数，表示位标志，不同的位位置代表不同的操作权限，能执行某一操作的位会被设为1;permission不同位位置对应的操作在Permission类设置
    permissions = db.Column(db.Integer)

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    
    '''Python中3种方式定义类方法, 常规方式, @classmethod修饰方式, @staticmethod修饰方式.  
       普通的类方法foo()需要通过self参数隐式的传递当前类对象的实例。 
       classmethod修饰的方法class_foo()需要通过cls参数传递当前类对象。
       @staticmethod修饰的方法定义与普通函数是一样的。'''
    @staticmethod
    def insert_roles():
    #完成将角色添加至数据库中,完成将角色添加至数据库中,查找某一角色是否在数据库中（roles）,如果不存在则增加这个角色
        roles = {
            #普通用户，可以写文章，关注用户，评论他人文章
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            #协管员：增加管理他人评论的权限
            'Moderator': [Permission.FOLLOW, Permission.COMMENT,Permission.WRITE, Permission.MODERATE],
            #管理员：具有所有权限，包括修改其他用户所属角色的权限
            'Administrator': [Permission.FOLLOW, Permission.COMMENT,Permission.WRITE, Permission.MODERATE,Permission.ADMIN],
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()   #重置该角色权限位为0
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):   #检查是否有perm权限
        return self.permissions & perm == perm
###

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64),unique=True,index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)   
    name = db.Column(db.String(64))      #新增真实姓名，所在地，自我介绍，注册日期，最后访问日期
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())      #db.String和db.Text区别在于后者不需要指定最大长度
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)    #default可接受函数作为默认值，每次需要生成默认值时，就调用指定函数
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)       #这两个值的默认值都是用户注册时的时间


    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

###ping方法每次用户访问网站时都会调用该方法，刷新最后使用时间
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

###用户注册账户时，会被赋予默认的用户角色，但是管理员在最开始就被赋予“管理员”角色，所以将管理员邮箱存入环境变量中，只要该邮箱出现在注册请求中，就被赋予正确角色
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

###

    @property    #表示密码为空，不可读
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

####邮箱验证加密处理
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)   #实例一个TimedJSONWebSignatureSerializer类的对象，才能调用dumps和loads方法
        return s.dumps({'confirm': self.id}).decode('utf-8')   #生成当前请求认证的id的加密签名

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        #检验令牌准确性
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True   #通过了令牌的验证之后，更改该属性为true
        db.session.add(self)
        return True
###
        
###通过邮箱重置密码
    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True
###

###修改邮箱
    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email}).decode('utf-8')

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True
###

###在User中添加辅助方法，检查是否有指定权限
    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)
###

    def __repr__(self):
        return '<User %r>' % self.username


###
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser
###

#flask-login需要程序实现一个回调函数，根据不同标识符加载用户信息,是用来，当用户有保存过信息时自动写入用户信息的吗？
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))    


    def __repr__(self):
        return '<User %r>' % self.username