from flask import Flask,render_template
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime

app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)

@app.route('/')
def user():
	return render_template('user.html',current_time=datetime.utcnow())

@app.route('/user/<name>')
def index(name):
	return render_template('index.html',name=name)

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'),404

if __name__=='__main__':
	app.run()
