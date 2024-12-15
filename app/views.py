from app import app, db, models, login_manager
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from .models import User, Film, Genre, film_genre, FilmRating, Followers
from .forms import ReviewForm, LoginForm, SignupForm, FindFilmForm, FindFriends, ShowLikedForm
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.orm import joinedload
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

import json
import csv

def data_csv_into_db():
    # dataset from F. Maxwell Harper and Joseph A. Konstan. 2015. The MovieLens Datasets: History and Context. ACM Transactions on Interactive Intelligent Systems (TiiS) 5, 4: 19:1–19:19. <https://doi.org/10.1145/2827872>
    file = 'app/data/movies.csv'
    with open(file, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) > 1:

                # structure of csv is title and year, genre (multiple separated by | ), images path
                title_year = row[1]
                genre_row = row[2]
                image_path = row[3]

                title_year= title_year.strip()
                genres = genre_row.split('|')

                film = Film(title=title_year, image=image_path)
                db.session.add(film)

                for genre_name in genres:
                    genre = Genre.query.filter_by(name=genre_name).first()
                    if not genre:
                        genre = Genre(name=genre_name)
                        db.session.add(genre)
                    if genre not in film.genre: 
                        film.genre.append(genre)
            
        db.session.commit()

    
@app.route('/', methods=['GET','POST'])
def movies():
    form = FindFilmForm()
    # filter films by the genre chosen in the combobox
    films = Film.query.all()
    form.genre.choices = [(genre.id, genre.name) for genre in Genre.query.all()]
    if form.validate_on_submit():
        chosen_genre = form.genre.data
        # join film table with film_genre table where the films are of the genre chosen
        films = Film.query.join(film_genre).filter(film_genre.c.genre_id == chosen_genre).all()
    else:
        films = Film.query.all()
    return render_template('films.html', title='Movies', form=form, films=films)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('profile') )
        else:
            flash('Username or password was invalid. Please try again.')
            return redirect(url_for('login') )
            
    return render_template('login.html', title='Login', form=form )

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        if form.password.data != form.confirm_password.data:
            flash('Passwords do not match.')
            return redirect(url_for('signup') )
        else:
            username_exists = User.query.filter_by(username=form.username.data).first()
            email_exists = User.query.filter_by(email=form.email.data).first()
            if username_exists:
                flash('Sorry this username is already taken! Try a different one.')
                return redirect(url_for('signup') )
            elif email_exists:
                flash('You already have an account registered with this email.')
                return redirect(url_for('signup') )
            else:
                hashed_password = generate_password_hash(form.password.data)
                new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                return redirect(url_for('profile') )
    
    return render_template('signup.html', title='Signup', form=form )

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    # query 3 reviews that the current user has created and order by most recent, according to the date watched
    users_films = FilmRating.query.filter_by(user_id=current_user.user_id).options(joinedload(FilmRating.film).joinedload(Film.genre)).order_by(FilmRating.date.desc()).limit(3).all()

    reviewed_films = [
        { 
            "film": {
                "title": reviews.film.title,
                # genres appear in a list separated by comas
                "genres": ", ".join([genre.name for genre in reviews.film.genre]),
                "image": reviews.film.image,
            },
            "rating": reviews.rating,
            "comment": reviews.comment,
            "date": reviews.date,
        }
        for reviews in users_films
    ]

    userId = User.query.get(current_user.user_id)

    # get all accounts that the current user follows
    following_ids = [account.user_id for account in Followers.query.filter_by(follower_id=current_user.user_id).all()]

    #queries 4 of the most recent reviews made by who the user is following
    followings_reviews = FilmRating.query.filter(FilmRating.user_id.in_(following_ids)).options(joinedload(FilmRating.film),joinedload(FilmRating.user)).order_by(FilmRating.date.desc()).limit(4).all()

    following_reviewed = [
        { 
            "film": {
                "title": reviews.film.title,
                "image": reviews.film.image,
            },
            "rating": reviews.rating,

            "user": {
                "username": reviews.user.username,
            }
        }
        for reviews in followings_reviews
    ]

    return render_template('profile.html', title='Profile', reviewed_films=reviewed_films, follower_count=userId.follower_count, following_count=userId.following_count, following_reviewed=following_reviewed)

@app.route('/liked', methods=['POST'])
def like_film():
    if request.method == 'POST':
        data = request.get_json()
        print(f"Received data: {data}")
        liked = data.get('liked')
        film_ID = data.get('film_id')

        liked_film = Film.query.get(film_ID)
        if liked == 1:
            if liked_film:
                liked_film.liked = 1
                db.session.commit()
        else:
            liked_film.liked = 0
            db.session.commit()
        return jsonify({'status':'OK','liked': liked_film.liked}), 200

@app.route('/watchlist', methods=['GET','POST'])
def watchlist():
    form = ShowLikedForm()
    form.watchlist.choices = [(1, 'Watchlist')]

    if form.validate_on_submit():
        films = Film.query.filter_by(liked = 1).all()
    else:
        films = Film.query.all()
        
    return render_template('watchlist.html', title='Watchlist', form=form, films=films)

@app.route('/reviews', methods=['GET', 'POST'])
@login_required
def reviews():
    form = ReviewForm()

    form.title.choices = [(film.film_id, film.title) for film in Film.query.all()]

    if request.method == 'POST':
        chosen_title = request.form.get('title')
        films = Film.query.filter_by(film_id=chosen_title).first()
        rated = request.form.get('rating')
        rated_film = FilmRating(user_id=current_user.user_id, film_id=films.film_id, rating=rated, date = form.watched.data, comment = form.comment.data)
        db.session.add(rated_film)
        db.session.commit()
        return redirect('/profile')
            
    return render_template('reviews.html', title='Reviews', form=form, films=None)

@app.route('/find_friends',  methods=['GET', 'POST'])
@login_required
def find_friends():

    form = FindFriends()
    username = []

    if form.validate_on_submit():
        user_input = form.search.data

        if user_input:
            # finds all usernames similar to what has been inputted
            username = User.query.filter((User.username.ilike(f'%{user_input}%'))).all()
            if not username:
                flash("No users found")
                return redirect(url_for('find_friends'))
        
    return render_template('search.html', title='Find Friends', username=username, form=form)

@app.route('/add_friends/<int:user_id>',  methods=['GET', 'POST'])
@login_required
def add_friends(user_id):

    if request.method == 'POST':
        already_following = Followers.query.filter_by(user_id=user_id, follower_id=current_user.user_id).first()
        if already_following:
            flash("You are already following this user")
            return redirect(url_for('profile'))
        
        new_following = Followers(user_id=user_id, follower_id=current_user.user_id)
        db.session.add(new_following)
        db.session.commit()
        return redirect(url_for('profile'))
    
    return render_template('search.html', title='Find Friends')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)