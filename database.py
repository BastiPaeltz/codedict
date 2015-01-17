"""Defines the data processing / handling using local sqlite3 database

 
"""

import sqlite3



def establish_db_connection():
	try:
		db = sqlite3.connect('codedict.DB')
	except sqlite3.DatabaseError:
		print "Database is encrypted or not a DB file."
		return False
	return db	


def change_content(content):
	"""Changes content of the database.

	"""

	db = establish_db_connection()
	if db:
		try:
			with db:
				db.execute('''
			    	UPDATE ? SET ? = ? WHERE use_case = ?
			    '''),((content['language'], content['attribute'], 
			    	content['data'], content['use_case']))
		except sqlite3.IntegrityError:
			pass
		db.close()
		return True
	else:
		print "Error while reaching DB."
		return False


def add_content(content):
	"""Adds content to the database.

	"""

	db = establish_db_connection()
	if db:
		try:
			with db:
				db.execute('''
			    	CREATE table IF NOT EXISTS {0} (id INTEGER PRIMARY KEY, 
			    		use_case TEXT, command TEXT, comment TEXT, code TEXT)
				'''.format(content['language']))
				
				db.execute('''
			    	INSERT INTO {0} (use_case,
			                   command, comment)VALUES(?, ?, ?)
				'''.format(content['language']), (content['use_case'], 
					content['command'], content['comment']))

		#TODO perform proper exception handling
		except sqlite3.IntegrityError:
			print "Cant add element twice"
			return False

		db.close()
		return True		
	else:
		print "Error while reaching DB."
		return False


def retrieve_content(location, requested_content=""):
	"""Retrieves content from the DB.

	"""

	db = establish_db_connection()
	if db:
		all_results = db.execute('''
		    SELECT command, ? from ?  where use_case = ?
		    ''',(requested_content, location['language'], location['use_case']))
		print all_results
		return (all_results, location)
	else:
		print "Error while reaching DB."
		return False
	
		