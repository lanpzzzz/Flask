#!usr/bin/env python
#-*- coding:utf-8 -*-
from flask import Blueprint

main = Blueprint('main',__name__)

from . import views,errors
from ..models import Permission

#为避免在每次调用render_template()时多添加一个模板参数，使用上下文处理器。
@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)