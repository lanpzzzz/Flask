#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template, session, redirect, url_for,flash
from flask_script import Shell
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail,Message
from threading import Thread

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
	'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
#配置Mail使用Gmail
app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
#在bash中配置环境变量MAIL_USERNAME和MAIL_PASSWORD，这是发件人邮箱账号和密码，要开启smtp授权
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['FLASKY_MAIL_SENDER']='Flasky Admin <532891679@qq.com>'
#发送的邮件中显示内容的前缀
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
#在bash中配置环境变量FLASKY_ADMIN为收件人邮箱地址
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')


bootstrap = Bootstrap(app)
moment = Moment(app)    #加入Flask-Moment扩展，可以在浏览器中渲染时间和日期# -*- coding: UTF-8 -*-
db = SQLAlchemy(app)
migrate = Migrate(app,db)    #Flask中集成的轻量级包装的Alembic数据库迁移框架,未实现
mail = Mail(app)    #

class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)     #创建User表
	username = db.Column(db.String(64), unique=True, index=True)
	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))    #设置外键是roles中的id

	def __repr__(self):
		return '<User %r>' % self.username     #当打印这个表格实例化的对象的时候会自动调用该函数

class Role(db.Model):
	__tablename__ = 'roles'
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(64),unique=True)
	users = db.relationship('User',backref='role',lazy='dynamic')    #对于一个Role类的实例，其user属性返回的是与角色想关联的用户组成的列表

	def __repr__(self):
		return '<Role %r>' % self.name 

def send_async_email(app,msg):
	#激活程序上下文
	with app.app_context():
		mail.send(msg)

def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    #纯文本正文,为什么要用两个
    msg.body = render_template(template + '.txt', **kwargs)
    #富文本正文，富文本可以对选中的部分单独设置字体、字形、字号、颜色。这里对动态参数部分设置了字体
    msg.html = render_template(template + '.html', **kwargs)
    #把send函数移到后台线程中，避免处理请求中出现不必要的延迟
    thr = Thread(target=send_async_email,args=[app,msg])
    thr.start()
    return thr

class NameForm(FlaskForm):
	#参数validators中指定由验证函数组成的列表，在接收用户提交的数据前进行验证，Required()用来确保提交的字段不为空 
	name=StringField('What is you name?',validators=[DataRequired()])   
	submit=SubmitField('Submit')

def make_shell_context():
	return dict(db=db, User=User, Role=Role)      #为shell命令注册一个make_context回调函数，回调函数中返回shell中需要导入的数据库实例和模型

@app.route('/',methods=['GET','POST'])
def index():
	form = NameForm()   #创建一个NameForm()类实例用于表示表单,存放当前键入的表单中的数据，目前只有name属性，和一个提交按钮
	if form.validate_on_submit():
		old_name = session.get('name')
		if old_name is not None and old_name != form.name.data:
			flash('Look like you have changed your name!')     #提醒用户状态发生变化，可以是确认、警告、错误提醒
		if User.query.filter_by(username=form.name.data).first() is None:    #筛选数据库中是否存入了当前键入的名字
			user = User(username=form.name.data)
			db.session.add(user)
			db.session.commit()
			session['known'] = False    #添加Known关键字参数，增加界面显示内容
			if app.config['FLASKY_ADMIN']:
				#传入收件人地址，邮件主题（题目），渲染邮件正文的模板，关键字参数列表（这里传入动态变量user，就是每接收一个新的名字就会发送一个邮件）
				send_email(app.config['FLASKY_ADMIN'], 'New User','mail/new_user', user=user)  
		else:
			session['known'] = True
		session['name']=form.name.data
		form.name.data = ''
		return redirect(url_for('index'))    #重定向当当前URL，不过重定向后的方法为GET，消除了刷新网址出现的错误
	return render_template('index.html', form=form, name=session.get('name'),known=session.get('known', False),current_time=datetime.utcnow())    #渲染界面，传入动态参数

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'),404

if __name__=='__main__':
	app.run()
