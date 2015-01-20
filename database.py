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
			    	UPDATE {0} SET {1} = ? WHERE use_case = ?
			    '''.format(content['<language>'], content['<attribute>']), (content['data']
			    , content['<use_case>']))
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
	print "DB",db
	if db:
		try:
			with db:
				db.execute('''
			    	CREATE table IF NOT EXISTS {0} (id INTEGER PRIMARY KEY, 
			    		use_case TEXT, command TEXT, comment TEXT, code TEXT)
				'''.format(content['language']))

				print "Created table", content['language']
		
				row = db.execute('''
			    	INSERT INTO {0} (use_case,
			                   command, comment)VALUES(?, ?, ?)
				'''.format(content['language']),((content['use_case'], 
					content['command'], content['comment'])))

				for items in row: 
					print "Row", items
		#TODO perform proper exception handling
		except sqlite3.IntegrityError:
			print "Cant add element twice"
			return False

		db.close()
		return True		
	else:
		print "Error while reaching DB."
		return False


def retrieve_extended_content(location):
	"""Retrieves command, comment from the DB.

	"""

	db = establish_db_connection()
	if db:
		all_results = []
		db_execute = db.execute('''
		    SELECT command, comment from {0} where use_case = ?
		    '''.format(location['<language>']), (location['<use_case>'],))
		for row in db_execute:
			all_results.append(row)
		db.close()	
		return (all_results, location)
	else:
		print "Error while reaching DB."
		return False


def retrieve_all_content(location):
	"""Retrieves all content for 1 specific use_case from the DB.

	"""

	db = establish_db_connection()
	if db:
		all_results = []
		db_execute = db.execute('''
		    SELECT * from {0} WHERE use_case = ? 
		    '''.format(location['<language>']), (location['<use_case>'],))
		for row in db_execute:
			all_results.append(row)
		db.close()	
		return (all_results, location)
	else:
		print "Error while reaching DB."
		return False


def retrieve_lang_content(location):
	"""Retrieves content for 1 specified language from the DB.

	"""

	db = establish_db_connection()
	if db:
		all_results = []
		db_execute = db.execute('''
		    SELECT command, use_case from {0} 
		    '''.format(location['<language>']))
		for row in db_execute:
			all_results.append(row)
		db.close()	
		return (all_results, location)
	else:
		print "Error while reaching DB."
		return False	
		

def retrieve_content(location):
	"""Retrieves basic content (command) for 1 use_case from the DB.

	"""

	db = establish_db_connection()
	if db:
		all_results = []
		db_execute = db.execute('''
		    SELECT command from {0} where use_case = ? 
		    '''.format(location['<language>']), (location['<use_case>'],))
		for row in db_execute:
			all_results.append(row)
		db.close()	
		return (all_results, location)
	else:
		print "Error while reaching DB."
		return False
