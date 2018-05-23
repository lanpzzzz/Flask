#!usr/bin/env python 
# -*- coding:utf-8 -*-
from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from . import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    #纯文本正文,为什么要用两个
    msg.body = render_template(template + '.txt', **kwargs)
    #富文本正文，富文本可以对选中的部分单独设置字体、字形、字号、颜色。这里对动态参数部分设置了字体
    msg.html = render_template(template + '.html', **kwargs)
    #把send函数移到后台线程中，避免处理请求中出现不必要的延迟
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
