"""Defines the data processing / handling using local sqlite3 database

 
"""


import sqlite3


def establish_db_connection():
	try:
		db = sqlite3.connect('codedict.DB')
	except sqlite3.DatabaseError:
		print "Database is encrypted or not a DB file."
		return False
	else: return db	



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
		#TODO PROPER EXCEPTION HANDLING
		db.close()
		return True

def add_content(content):
	"""Adds content to the database.

	"""

	db = establish_db_connection()
	if db:
		try:
			with db:
				db.execute('''
			    	CREATE table IF NOT EXISTS TableName = ? (id INTEGER PRIMARY KEY, 
			    		use_case TEXT, command TEXT, comment TEXT, code TEXT)
				''', (content['language'],))
		
				db.execute('''
			    	INSERT INTO TableName = ? (use_case,
			                   command, comment)VALUES(?, ?, ?))
				''', ((content['language'], content['use_case'], 
					content['command'], content['comment'])))

		#TODO perform proper exception handling
		except sqlite3.IntegrityError:
			print "Cant add element twice"
			return False

		db.close()
		return True		


def retrieve_content(location, requested_content="*"):
	"""Retrieves content from the DB.

	"""

	db = establish_db_connection()
	if db:
		db.execute('''
		    	SELECT command from ?  where 




	
		