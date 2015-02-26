"""Defines the data processing / handling using local sqlite3 database

 
"""

import sqlite3
from textwrap import fill




def establish_db_connection():
	"""Establishes the connection to the DB."""

	try:
		db = sqlite3.connect('../res/codedict.DB')
	except sqlite3.DatabaseError:
		print "Database is encrypted or not a DB file."
		return False
	return db	


def update_content(content):
	"""Changes content of the database.

	"""

	db = establish_db_connection() 
	if db:
		try:
			with db:
				db.execute('''
			    	UPDATE {0} SET {1} = ? WHERE use_case = ?
			    '''.format(content['<language>'], 
			    	content['<attribute>']), 
			    	(content['data'], 
			    	content['<use_case>']))
		except sqlite3.IntegrityError:
			pass
		db.close()
		return True
	else:
		print "Error while reaching DB."
		return False


def create_table(lang):
	"""Creates a table for a specific language in the DB.

	"""

	db = establish_db_connection()
	
	if db:
		try:
			with db:
				db.execute('''
			    	CREATE table IF NOT EXISTS {0} (id INTEGER PRIMARY KEY, 
			    		use_case TEXT, command TEXT, comment TEXT, code TEXT)
				'''.format(lang))
				print "Created table", lang
		except sqlite3.IntegrityError:
			print "Cant add element twice"
			return False
		db.close()
		return True		
	else:
		print "Error while reaching DB."
		return False


def add_content(values, location, multiple_insert=False):
	"""Adds content to the database.

	"""

	db = establish_db_connection()
	if db:
		try:
			if not multiple_insert:
				with db:
					row = db.execute('''
				    	INSERT or REPLACE into {0} 
				    	(use_case, command, comment)
				    	VALUES(?, ?, ?)
					'''.format(location), ( 
						(values['use_case'], 
						values['command'], 
						values['comment'])))

					for items in row: 
						print "Row", items
			#TODO perform proper exception handling
				return True
			else:
				#File adding
				with db:
					for new_item in values:
						row = db.execute('''
					    	INSERT or REPLACE into {0} 
					    	(use_case, command, comment)
					    	VALUES(?, ?, ?)
						'''.format(location), 
							(fill(new_item[0], width=20), 
						 	 fill(new_item[1], width=25), 
						 	 fill(new_item[2], width=25)))

						for items in row: 
							print "Row", items	 
				return True


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
	all_results = []
	db = establish_db_connection()
	if db:
		db_execute = db.execute('''
		    SELECT command, comment FROM {0} where use_case LIKE ?
		    '''.format(location['<language>']), (location['<use_case>']+'%',))
		for count, row in enumerate(db_execute):
			all_results.append((count + 1, ) + row)
		db.close()	
		return all_results
	else:
		print "Error while reaching DB."
		return False


def retrieve_all_content(location):
	"""Retrieves all content for 1 specific use_case from the DB.

	"""
	all_results = []
	db = establish_db_connection()
	if db:
		if check_for_table_existence(location['<language>'], db):
			db_execute = db.execute('''
			    SELECT use_case, command, comment FROM {0} WHERE use_case LIKE ?
			    '''.format(location['<language>']), (location['<use_case>']+'%',))
			for count, row in enumerate(db_execute):
				all_results.append((count + 1, ) + row)
			db.close()	
			return all_results
		else:
			print "No such table"
			return False
	else:
		print "Error while reaching DB."
		return False


def retrieve_lang_content(location):
	"""Retrieves content for 1 specified language from the DB.

	"""
	all_results = []
	db = establish_db_connection()
	if db:
		if check_for_table_existence(location['<language>'], db):
			db_execute = db.execute('''
			    SELECT command, use_case FROM {0} 
			    '''.format(location['<language>']))
			for count, row in enumerate(db_execute):
				all_results.append((count + 1, ) + row)
			db.close()	
			return all_results
		else:
			print "No such table"
			return False
	else:
		print "Error while reaching DB."
		return False	
		

def retrieve_content(location):
	"""Retrieves basic content (command) for 1 use_case from the DB.

	"""
	all_results = []
	db = establish_db_connection()
	if db:
		if check_for_table_existence(location['<language>'], db):
			db_execute = db.execute('''
			    SELECT use_case, command FROM {0} WHERE use_case LIKE ? 
			    '''.format(location['<language>']), (location['<use_case>']+'%',))
			for count, row in enumerate(db_execute):
				all_results.append((count + 1, ) + row)
			db.close()	
			return all_results
		else:
			print "No such table"
	else:
		print "Error while reaching DB."
		return False


def retrieve_code(location):
	"""Retrieves code for 1 use_case from the DB.

	"""
	all_results = []
	db = establish_db_connection() 
	if db:
		if check_for_table_existence(location['<language>'], db):
			db_execute = db.execute('''
			    SELECT code FROM {0} WHERE use_case = ? 
			    '''.format(location['<language>']), (location['<use_case>'],))
			for count, row in enumerate(db_execute):
				all_results.append((count + 1, ) + row)
			db.close()	
			return all_results
		else:
			print "No such table"
			return False
	else:
		print "Error while reaching DB."
		return False


def check_for_table_existence(table_name, database):
	"""Checks if a table exists.

	"""
	db_execute = database.execute('''
		    SELECT name FROM sqlite_master WHERE type='table' AND name=?
		    ''', (table_name, ))
	return db_execute.fetchone()

