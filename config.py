import os
_basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = True

SECRET_KEY = 'Wow, such secret'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

THREADS_PER_PAGE = 8
