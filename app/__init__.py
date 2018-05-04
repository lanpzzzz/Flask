#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_login import LoginManager

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()

#Flask-Login是非常有用的小型扩展，管理用户认证状态，在这里进行初始化
login_manager = LoginManager()
login_manager.session_protection = 'strong'    #选择安全等级
login_manager.login_view = 'auth.login'    #设置登录页面的端点



def create_app(config_name):
    app = Flask(__name__)
    #从配置.py文件中导入定义的config字典，这里的config_name是命令行配置的FLASK_CONFIG参数或者默认模式
    #选择当前配置参数是development,testing,production中哪种模式，如果环境中未进行配置则选择默认的development配置
    app.config.from_object(config[config_name])    #配置程序配置
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    #把蓝本注册到程序上
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint,url_prefix='/auth')

    return app