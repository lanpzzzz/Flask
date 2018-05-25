#!usr/bin/env python
#-*- coding:utf-8 -*-
from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission      #Permission类中是要支持的用户角色已及定义角色使用的权限位


def permission_required(permission):
	#装饰器的本质就是一个函数，所有想要自定义一个装饰器，首先自定义一个函数.传入的是函数
    def decorator(f):
    	#将被修饰的函数(wrapped) 的一些属性值赋值给修饰器函数(wrapper)，最终让属性的显示更符合我们的直觉
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)    #如果用户不具有指定权限，则返回403错误码
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    return permission_required(Permission.ADMIN)(f)