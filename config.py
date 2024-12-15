import os, secrets

salt = secrets.SystemRandom().getrandbits(128)

WTF_CSRF_ENABLED = True
SECRET_KEY = 'a-very-secret-secret'

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = True
SECURITY_PASSWORD_SALT = salt
SECURITY_PASSWORD_HASH = "bcrypt"