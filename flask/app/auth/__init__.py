#!usr/bin/env python
# -*- coding:utf-8 -*-
#创建认证蓝本，不同的程序功能要使用不同的蓝本，蓝本保存在同名的python包中
from flask import Blueprint

auth = Blueprint('auth',__name__)

from . import views