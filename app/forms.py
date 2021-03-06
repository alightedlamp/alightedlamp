from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length
from app.models import User

class EditForm(Form):
    nickname = StringField('nickname', validators=[DataRequired()])
    instagram = StringField('instagram', validators=[Length(min=0, max=20)])
    twitter = StringField('twitter', validators=[Length(min=0, max=20)])
    about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])

    def __init__(self, original_nickname, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname

    def validate(self):
        if not Form.validate(self):
            return False
        if self.nickname.data == self.original_nickname:
            return True
        user = User.query.filter_by(nickname=self.nickname.data).first()
        if user != None:
            self.nickname.errors.append('This nickname is already in use. Please choose another one.')
            return False
        return True

class PostForm(Form):
    title = StringField('title', validators=[DataRequired()], render_kw={"placeholder": "Title"})
    post = TextAreaField('post', validators=[DataRequired()], render_kw={"placeholder": "What's going on?"})