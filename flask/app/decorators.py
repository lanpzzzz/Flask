#!usr/bin/env python
#-*- coding:utf-8 -*-
from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission


def permission_required(permission):
	#装饰器的本质就是一个函数，所有想要自定义一个装饰器，首先自定义一个函数
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    return permission_required(Permission.ADMIN)(f)