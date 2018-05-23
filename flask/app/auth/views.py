#!usr/bin/env python 
# -*- coding:utf-8 -*-
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..models import User
from ..email import send_email
from .forms import LoginForm, RegistrationForm,ChangePasswordForm

####这句的意思，字面上理解是，在app的request响应之前，先如何如何............
@auth.before_app_request 
def before_request():
	#默认confirmed属性是False的,，只有通过邮箱验证函数之后，该属性才被改为true
	##而且，request的网址不是以auth.和static开头的
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint \
            and request.blueprint != 'auth' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))    #就返回到未确认的一个路由


@auth.route('/unconfirmed')     #处理未确认的路由
def unconfirmed():
	#已确认的用户经过上面钩子不是已经排除了吗？怎么还会到这里的路由来
    if current_user.is_anonymous or current_user.confirmed:    #如果用户是非普通用户(is_anonymous对普通用户返回False)，或者已确认的，则返回主页
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')
###

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
        token = user.generate_confirmation_token()
        send_email(user.email,'Confirm Your Account','auth/email/confirm',user=user,token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('auth.login'))  #不能直接转到登录之后的状态界面，因为index.html中用的current_user是有Flask-Login定义在视图函数和模板中自动可用，这个视图函数和模板指的是只有login下的模板吗？为什么这里用就不能判断为真。
    return render_template('auth/register.html', form=form)

###
@auth.route('/confirm/<token>')
@login_required    #保护路由，要求你必须是在登陆状态才能访问这个页面
def confirm(token):
    if current_user.confirmed:    #如果用户的状态已经是confirmed的了，那直接范围首页了
        return redirect(url_for('main.index'))
    if current_user.confirm(token):   #如果用户通过这个页面的访问，调用confirm函数并返回True了，那成功验证
        db.session.commit()
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))

#有时候，如果你的验证令牌已经过期了，那我们需要重新发送一份邮件来确认，那怎么办呢？再做一个路由......来重新发送邮件
@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account','auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))
###


@auth.route('/change-password',methods = ['GET','POST'])
@login_required
def change_password():
	form = ChangePasswordForm()
	if form.validate_on_submit():
		#先判断当前用户的旧密码是否正确
		if current_user.verify_password(form.old_password.data):
			current_user.password = form.password.data
			db.session.add(current_user)
			db.session.commit()
			flash('Your password has been update')
			return redirect(url_for('main.index'))
		else:
			flash('Invalid password')
	return render_template("auth/change_password.html",form=form)



