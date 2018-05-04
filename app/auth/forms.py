from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,BooleanField,SubmitField,PasswordField
from wtforms.validators import Required,Email,Length,Regexp


class NameForm(FlaskForm):
	email = StringField('Email',validators=[Required(),Length(1,64),Email()])
	password = PasswordField('Password',validators=[Required(),Length(1,64),Regexp9('^[A-Za-z][A-Za-z0-9_.]*$',0,'Usernames must have only letters','numbers,dots or underscores')])
	remember_me = BooleanField('Keep me logged in ')
	submit = SubmitField('Log In')