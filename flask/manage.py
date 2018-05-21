#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from app import create_app,db
from app.models import User,Role
from flask_script import Manager,Shell
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')  
manager = Manager(app)    #后可以使用一组基本命令行选项
migrate = Migrate(app,db)

@manager.command
def test():
	"""Run the unit tests."""
	import unittest
	tests = unittest.TestLoader().discover('tests')
	unittest.TextTestRunner(verbosity=2).run(tests)

def make_shell_context():    #为shell命令注册一个回调函数，添加上下文
	return dict(app=app,db=db,User=User,Role=Role)    #返回创建的字典对象

manager.add_command("shell",Shell(make_context=make_shell_context))   #添加自定义命令，即运行时可以增加自定义的命令字符,即每次直接加shell命令后即可导入数据库实例、模型等
manager.add_command('db',MigrateCommand)

if __name__=='__main__':
	manager.run()