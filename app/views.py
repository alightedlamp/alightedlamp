import flask
from flask import render_template, flash, redirect, session, url_for, request, g, session as flask_session
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, login_manager
from forms import EditForm, PostForm
from models import User, Post
from .models import User
from .forms import EditForm
from .handlers.auth_handler import get_google_auth
from config import Auth
from config import POSTS_PER_PAGE
from urllib2 import HTTPError
from datetime import datetime
import json

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
def index(page=1):
    if g.user.is_authenticated:
        posts = g.user.followed_posts().order_by(Post.timestamp.desc()).paginate(page, POSTS_PER_PAGE, False)
        return render_template('index.html',
                               title='Home',
                               posts=posts)
    else:
        posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, POSTS_PER_PAGE, False)
        google = get_google_auth()
        auth_url, state = google.authorization_url(
            Auth.AUTH_URI, access_type='offline')
        session['oauth_state'] = state
        return render_template('index.html',
                               title='Home',
                               posts=posts,
                               auth_url=auth_url)


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


'''@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    google = get_google_auth()
    auth_url, state = google.authorization_url(
        Auth.AUTH_URI, access_type='offline')
    session['oauth_state'] = state
    return render_template('login.html', auth_url=auth_url)
'''


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
        return redirect(url_for('index'))
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
            # user.avatar = user_data['picture']
            nickname = user_data['name'] or user_data['email'].split('@')[0].capitalize()
            nickname = User.make_unique_nickname(nickname)
            if user is None:
                user = User(
                    nickname=nickname,
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
@app.route('/user/<nickname>/<int:page>')
def user(nickname, page=1):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User %s not found. :/' % nickname, 'alert-warning')
        return redirect(url_for('index'))
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(page, POSTS_PER_PAGE, False)
    return render_template('user.html',
                           user=user,
                           posts=posts)


# how to query for all users?
@app.route('/users')
def users():
    users = User.query.order_by(User.nickname.asc()).all()
    return render_template('users.html',
                           users=users)


@app.route('/user/<nickname>/edit', methods=['GET', 'POST'])
@login_required
def edit(nickname):
    form = EditForm(g.user.nickname)
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        g.user.instagram_user = form.instagram.data
        g.user.twitter_user = form.twitter.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your post has been edited! :)', 'alert-success')
        return redirect(url_for('user', nickname=nickname))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
        form.instagram.data = g.user.instagram_user
        form.twitter.data = g.user.twitter_user
    return render_template('edit.html', form=form)


@app.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, timestamp=datetime.utcnow(), author=g.user, title=form.title.data)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live! :)', 'alert-success')
        return redirect(url_for('index'))
    return render_template('new.html', form=form)


@app.route('/post/<post_id>', methods=['GET'])
@login_required
def view_post(post_id):
    post = Post.query.filter_by(id=post_id).first()
    if post is None:
        flash('Post %s not found. :(' % post_id, 'alert-warning')
        return redirect(url_for('index'))
    return render_template('view-post.html',
                           post=post)


@app.route('/post/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.filter_by(id=id).first()
    nickname = g.user.nickname
    if g.user.id == post.user_id:
        form = PostForm()
        if form.validate_on_submit():
            post.title = form.title.data
            post.body = form.post.data
            db.session.add(post)
            db.session.commit()
            flash('Your changes have been saved. :)', 'alert-success')
            return redirect(url_for('edit_post', id=post.id))
        else:
            form.title.data = post.title
            form.post.data = post.body
        return render_template('edit-post.html', form=form)
    else:
        flash('That isn\'t your post! >:O', 'alert-danger')
        return redirect(url_for('user', nickname=nickname))


@app.route('/post/delete/<id>', methods=['GET', 'POST'])
@login_required
def del_post(id):
    post = Post.query.filter_by(id=id).first()
    nickname = g.user.nickname
    if post is None:
        flash('Post %s not found.' % id, 'alert-warning')
        return redirect(url_for('user', nickname=nickname))
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted forever. :D', 'alert-success')
    return redirect(url_for('user', nickname=nickname))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User %s not found. :(' % nickname, 'alert-warning')
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t follow yourself! ;)', 'alert-warning')
        return redirect(url_for('user', nickname=nickname))
    u = g.user.follow(user)
    if u is None:
        flash('Cannot follow ' + nickname + '.', 'alert-warning')
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('You are now following ' + nickname + '! :D', 'alert-success')
    return redirect(url_for('user', nickname=nickname))


@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User %s not found.' % nickname, 'alert-warning')
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t unfollow yourself!', 'alert-warning')
        return redirect(url_for('user', nickname=nickname))
    u = g.user.unfollow(user)
    if u is None:
        flash('Cannot unfollow ' + nickname + '.', 'alert-warning')
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('You have stopped following ' + nickname + '.', 'alert-success')
    return redirect(url_for('user', nickname=nickname))


@app.route('/about')
def about():
    if g.user.is_authenticated:
        return render_template('about.html', title="About")
    else:
        google = get_google_auth()
        auth_url, state = google.authorization_url(
            Auth.AUTH_URI, access_type='offline')
        session['oauth_state'] = state
        return render_template('about.html',
                               title="About",
                               auth_url=auth_url)\


@app.route('/projects')
def projects():
    if g.user.is_authenticated:
        return render_template('projects.html', title="Projects")
    else:
        google = get_google_auth()
        auth_url, state = google.authorization_url(
            Auth.AUTH_URI, access_type='offline')
        session['oauth_state'] = state
        return render_template('projects.html',
                               title="Projects",
                               auth_url=auth_url)


@app.route('/studio')
def studio():
    if g.user.is_authenticated:
        return render_template('studio.html', title="The Studio")
    else:
        google = get_google_auth()
        auth_url, state = google.authorization_url(
            Auth.AUTH_URI, access_type='offline')
        session['oauth_state'] = state
        return render_template('studio.html',
                               title="The Studio",
                               auth_url=auth_url)
