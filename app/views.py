import flask
from flask import render_template, flash, redirect, session, url_for, request, g, session as flask_session
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, login_manager
from .models import User
from .forms import EditForm
from .handlers.auth_handler import get_google_auth
from config import Auth
from urllib2 import HTTPError
from datetime import datetime
import json

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

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()

@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    google = get_google_auth()
    auth_url, state = google.authorization_url(
        Auth.AUTH_URI, access_type='offline')
    session['oauth_state'] = state
    return render_template('login.html', auth_url=auth_url)

@app.route('/gCallback')
def callback():
    current_user = flask.g.user
    session = db.session

    # Redirect user to home page if already logged in.
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('index'))
    if 'error' in request.args:
        if request.args.get('error') == 'access_denied':
            return 'You denied access.'
        return 'Error encountered.'
    if 'code' not in request.args and 'state' not in request.args:
        return redirect(url_for('login'))
    else:
        # Execution reaches here when user has
        # successfully authenticated our app.
        google = get_google_auth(state=flask_session['oauth_state'])
        try:
            token = google.fetch_token(
                Auth.TOKEN_URI,
                client_secret=Auth.CLIENT_SECRET,
                authorization_response=request.url.replace('http://', 'https://'),
            )
        except HTTPError:
            return 'HTTPError occurred.'
        google = get_google_auth(token=token)
        # todo: cool stuff in here
        resp = google.get(Auth.USER_INFO)
        if resp.status_code == 200:
            user_data = resp.json()
            email = user_data['email']
            user = User.query.filter_by(email=email).first()
            if user is None:
                user = User(
                    nickname=user_data['name'] or user_data['email'].split('@')[0].capitalize(),
                    email=email,
                    avatar=user_data['picture']
                )
            user.tokens = json.dumps(token)
            session.add(user)
            session.commit()
            login_user(user)
            return redirect(url_for('index'))
        return 'Could not fetch your information.'

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/user/<nickname>')
@login_required
def user(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user == None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html',
                           user=user,
                           posts=posts)

@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm()
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('edit.html', form=form)