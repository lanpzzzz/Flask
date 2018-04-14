from flask import Flask,render_template
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import DataRequired


app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
bootstrap = Bootstrap(app)
moment = Moment(app)


class NameForm(FlaskForm):
	name=StringField('What is you name?',validators=[DataRequired()])
	submit=SubmitField('Submit')

@app.route('/',methods=['GET','POST'])
def user():
	name = None
	form = NameForm()
	if form.validate_on_submit():
		name = form.name.data
		form.name.data = ''
	return render_template('user.html',form=form,name=name,current_time=datetime.utcnow())

@app.route('/user/<name>')
def index(name):
	return render_template('index.html',name=name)

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'),404

if __name__=='__main__':
	app.run()
