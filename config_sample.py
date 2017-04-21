###########################################################
###############  DO NOT EDIT THIS SECTION!  ###############
###########################################################
import os

class User:
	def __init__(self, username, password, staff, account, balance):
		self.username = username
		self.password = password
		self.staff = staff
		self.account = account
		self.balance = balance

class Account:
	def __init__(self, id, pin):
		self.id = id
		self.pin = pin

###########################################################
####################  EDIT BELOW HERE  ####################
###########################################################
# General Configuration
DEBUG = True
THREADS_PER_PAGE = 8

# Database Configuration
SQLALCHEMY_DATABASE_URI = "mysql://user:pass@localhost:3306/bank"
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Slack Configuration
SLACK_ENABLED = False
SLACK_APIKEY = "xoxp-xx-xx-xx-xx"
SLACK_CHANNEL = "#bank"

# Bank Configuration
AMOUNT_PER_SERVICE_UP = 100
WHITE_TEAM_ACCOUNT = "3141592653"
TEAM_ACCOUNT_MAPPINGS = {
	1: Account("0000000001", "0000"),
	2: Account("0000000002", "0000"),
	3: Account("0000000003", "0000"),
	4: Account("0000000004", "0000"),
	5: Account("0000000005", "0000"),
	6: Account("0000000006", "0000"),
	7: Account("0000000007", "0000"),
	8: Account("0000000008", "0000"),
	9: Account("0000000009", "0000"),
	10: Account("0000000010", "0000")
}

# Team Configuration
TEAM_INITIAL_MONEY = 85000.00

# Account Configuration
ACCOUNTS = [
	User("staff", "staff", True, Account(WHITE_TEAM_ACCOUNT, "1234"), 1000000000.00),
	User("scoring", "scoring", True, Account("2000000000", "1234"), 0.0),
]

###########################################################
###############  DO NOT EDIT THIS SECTION!  ###############
###########################################################
# Build the rest of the accounts
for teamnum, account in TEAM_ACCOUNT_MAPPINGS.items():
	userpass = "team{}".format(teamnum)
	ACCOUNTS.append(User(userpass, userpass, False, account, TEAM_INITIAL_MONEY))