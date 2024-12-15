from app import db
from flask_login import UserMixin

# model describing user with relationships to film ratings that they create and followers
class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True, unique=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    rated_films = db.relationship('FilmRating', back_populates='user')
    follower = db.relationship('Followers', primaryjoin="or_(User.user_id==Followers.user_id, User.user_id==Followers.follower_id)")

    def get_id(self):
        return self.user_id

    def __repr__(self):
        return f'<User {self.username}>'
    
    # function that return the number of accounts that follow the current user
    @property
    def follower_count(self):
        return Followers.query.filter_by(user_id=self.user_id).count()
    
    # function that returns the number of accounts the current user follows
    @property
    def following_count(self):
        return Followers.query.filter_by(follower_id=self.user_id).count()

# model to decribe film with relationship to genre table and ratings
class Film(db.Model):
    film_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    image = db.Column(db.String(50))
    liked = db.Column(db.Integer, nullable=True)
    genre = db.relationship('Genre', secondary='film_genre', back_populates='film')
    ratings = db.relationship('FilmRating', back_populates='film')

# model to show film ratings and relationships to users and films to show what film was logged and by who
class FilmRating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    film_id = db.Column(db.Integer, db.ForeignKey('film.film_id'), nullable=False)
    rating = db.Column(db.Integer, default=0, nullable=False)
    date = db.Column(db.Date)
    comment = db.Column(db.Text, nullable=True)
    user = db.relationship('User', back_populates='rated_films')
    film = db.relationship('Film', back_populates='ratings')

# model that describes genre and the relationship to film table
class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    film = db.relationship('Film', secondary='film_genre', back_populates='genre') 

# association table that describes the association between a film having multiple genres
film_genre = db.Table(
    'film_genre',
    db.Column('film_id', db.Integer, db.ForeignKey('film.film_id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True)
)

# model that describes users following other users
class Followers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

    