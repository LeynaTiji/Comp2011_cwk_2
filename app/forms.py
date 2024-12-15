from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TextAreaField, IntegerField, PasswordField, EmailField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Email

class ReviewForm(FlaskForm):
    title = SelectField('Film Title', coerce=int, choices=[], validators=[DataRequired()])
    watched = DateField('Date Watched', validators=[DataRequired()])
    comment = TextAreaField('Comment')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=5, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=25)])

class SignupForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(min=5, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=25)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=6, max=25)])

class FindFilmForm(FlaskForm):
    genre = SelectField('Genre', coerce=int, choices=[])

class ShowLikedForm(FlaskForm):
    watchlist = SelectField('Watchlist', coerce=int, choices=[])

class FindFriends(FlaskForm):
    search = StringField('Search by username', render_kw={"placeholder": "Enter a username", "style": "width: 1000px; height: 50px"})
