import os
_basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = True

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

THREADS_PER_PAGE = 8

SLACK_POST_URI = 'https://hooks.slack.com/services/XXX/XXX/XXX'

WHITE_TEAM_ACCOUNT = '3141592653'

TEAM_ACCOUNT_MAPPINGS = {
	1: '0558761544',
	2: '2880676778',
	3: '3536003764',
	4: '0757044331',
	5: '8808713424',
	6: '5322655624',
	7: '5512862460',
	8: '7466280270',
	9: '8532806222',
	10: '3150788157'
}
