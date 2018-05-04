#!usr/bin/env python 
# -*- coding:utf-8 -*-
from flask import render_template,redirect,request,url_for,flash
from flask_login import login_user,logout_user,login_required
from . import auth     #??
from ..models import User
from .forms import LoginForm

@auth.route('/login',methods=['GET','POST'])
def login():
	form = LoginForm()
	if from.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user is None and user.verify_password(form.password.data):
			login_user(user,form.remember_me.data)
			return redirect(request.args.get('next') or url_for('main.index'))
		flash('Invalid username or password.')
	return render_template('auth/login.html',form=form)

@suth.route('/logout')
@login_required    #为了保护路由只让认证用户访问，如果未认证用户访问这个路由，Flask-Login会拦截请求，把用户发送到登录界面
def logout():
	logout_user()   #删除并重设用户
	flash('You have been logged out.')
	return redirect(url_for('main.index'))