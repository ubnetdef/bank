import os
_basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = False

SQLALCHEMY_DATABASE_URI = 'mysql://bank:734A696C85B29AD97FEE21D6B6@192.168.1.50/bank'
SQLALCHEMY_TRACK_MODIFICATIONS = False

THREADS_PER_PAGE = 8

SLACK_POST_URI = 'https://hooks.slack.com/services/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'