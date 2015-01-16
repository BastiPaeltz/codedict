"""Defines the data processing / handling using local sqlite3 database


"""


import sqlite3
import os

def check_db_existence(name):
	"""Checks if the DB has to be created first

	"""

	if name in os.listdir():
		print "DB is already created"
		return True
	else:
		print "Creating DB"
		if "error":
			return False
		else:
			return True


def setup_database(name):
	"""Creates the database, makes it ready for use

	"""

	if check_db_existence(name):
		connector = sqlite3.connect(name)
		return connector
	else: 
		print "An error has occured while creating the DB."
		return False


def add_content(location, content):
	"""Adds content to the database.

	"""

	connector = setup_database('database.db')
	if connector:
		print """
			Adding content {0} now to the DB
			""".format(content)
	else:
		print "An error has occured while Setting up DB."


def display_content(location, requested_content = None):
	"""Displays content from the DB.

	"""

	connector = setup_database('database.db')
	if connector:
		print """
			  Reading out {0} from DB now.
			  Flags = {1}
			  """.format(location, requested_content)
		return content
	else:
		print "An error has occured while setting up DB."
		return False