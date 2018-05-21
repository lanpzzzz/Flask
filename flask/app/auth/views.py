#!usr/bin/env python 
# -*- coding:utf-8 -*-
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..models import User
from ..email import send_email
from .forms import LoginForm, RegistrationForm

@auth.route('/login',methods=['GET','POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():  #当前提交的http请求为POST方法，且已经点了提交按钮
		user = User.query.filter_by(email=form.email.data).first()   #检查提交的表单中邮箱是否存在于数据库中，且密码是否正确
		if user is not None and user.verify_password(form.password.data):
			login_user(user,form.remember_me.data)   #根据传入参数，判断下次是否保持登录信息
			return redirect(request.args.get('next') or url_for('main.index'))   #按书中定义重定向到next参数中，如果访问的URL未授权（这是什么情况）则将原地址保存至next参数中，否则就重定向到首页。
		flash('Invalid username or password.')
	return render_template('auth/login.html',form=form)   #先GET方法得到login页面（只是渲染了以下form表格），账号密码都正确的话用POST方法重定向到index视图函数

@auth.route('/logout')
@login_required    #为了保护路由只让认证用户访问，如果未认证用户访问这个路由，Flask-Login会拦截请求，把用户发送到登录界面
def logout():
	logout_user()   #删除并重设用户
	flash('You have been logged out.')
	return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You can now login.')
        return redirect(url_for('auth.login'))  #不能直接转到登录之后的状态界面，因为index.html中用的current_user是有Flask-Login定义在视图函数和模板中自动可用，这个视图函数和模板指的是只有login下的模板吗？为什么这里用就不能判断为真。
    return render_template('auth/register.html', form=form)


