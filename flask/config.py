#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
basedir = os.path.abspath(os.path.dirname(__file__))

###邮箱不能注册为163邮箱，会出现错误
class Config:
	#hello.py中app.config中配置的参数
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    #终于邮件发送成功了，错在哪里？MAIL_SERVER改为qq邮箱的服务器地址和端口
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.qq.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    #重新配置MAIL_USERNAME和MAIL_PASSWORD粗心名字输错了.配置邮箱名和授权IMAP的授权码
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    #为什么每次都要重新设置一次密码，5/24又出现503错误
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    #FLASK_MAIL_SENDER直接照搬的代码，没有改。要改为发送邮件的邮箱
    FLASKY_MAIL_SENDER = 'Flasky Admin <532891679@qq.com>'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite://'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    
    'default': DevelopmentConfig
}