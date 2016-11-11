from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid
from .forms import LoginForm
from .models import User

@app.route('/')
@app.route('/index')
@login_required
def index():
	user = g.user
	posts = [
		{
			'author': {'nickname': 'Ryan'},
			'title': 'Nice affect, bro',
			'body': 'Some stuff about labyrinths and how they aren\'t the same thing as mazes'
		},
		{
			'author': {'nickname': 'Kevin'},
			'title': 'Talkin\' bout the weather',
			'body': 'Making art in the countryside'
		}
	]
	return render_template('index.html',
		title='Home',
		user=user,
		posts=posts)

@lm.user_loader
def load_user(id):
	return User.query.get(int(id))

@app.before_request
def before_request():
	g.user = current_user

@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
	if g.user is not None and g.user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		session['remember_me'] = form.remember_me.data
		return old.try_login(form.openid.data, ask_for=['nickname','email'])
	return render_template('login.html',
							title='Sign In',
							form=form,
							providers=app.config['OPENID_PROVIDERS'])