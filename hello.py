from flask import Flask,render_template
from flask.ext.bootstrap import Bootstrap

app = Flask(__name__)
bootstrap = Bootstrap(app)

@app.route('/')
def user():
	return render_template('user.html',comments=(1,2,3,4,1,2,3))

@app.route('/user/<name>')
def index(name):
	return render_template('index.html',name=name)

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'),404

if __name__=='__main__':
	app.run()
