"""Defines the data processing / handling using local sqlite3 database

 
"""

#import from standard library
import sqlite3



def establish_db_connection():
	"""Establishes the connection to the DB.
	   Returns: DB object or False
	"""

	try:
		db = sqlite3.connect('../res/codedict0_6.DB')
	except sqlite3.Error as error:
		print "A database error has occured: ", error
		return False
	return db	


def setup_database():
	"""Sets up the database for usage.

	"""
	
	db = establish_db_connection()
	if not db or not create_table(db):
		print "Error while reaching DB."
		return False
	
	if not create_table(db):
		print "Error while creating DB tables."
		return False
	return db


def create_table(db):
	"""Creates tables 'dictionary' and 'languages'.
       Returns: True or False
	"""

	try:
		with db:
			# create tables
			db.execute('''
		    	CREATE table IF NOT EXISTS Languages (id INTEGER PRIMARY KEY, 
		    		language TEXT)
			''')

			db.execute('''
		    	CREATE table IF NOT EXISTS Dictionary (id INTEGER PRIMARY KEY, languageID INTEGER, 
		    		use_case TEXT, command TEXT, comment TEXT, links TEXT, code TEXT)
			''')

	except sqlite3.Error as error:
		print "A database error has occured: ", error
		return False
	return True	


def delete_content(values):
	"""Changes content of the database.
	   Returns: True or False
	"""

	db = setup_database() 

	if not db:
		print "Error while reaching DB."
		return False
	try:
		with db:
			# update database
			db.execute('''
		    	DELETE from Dictionary WHERE use_case = ? AND languageID = 
		    	(SELECT id from Languages where language = ?)
		    ''', (values['<use_case>'], values['<language>']))
	except sqlite3.Error as error:
		print "A database error has occured: ", error
		return False
	return True


def update_content(values):
	"""Changes content of the database.
	   Returns: True or False
	"""

	db = setup_database() 
	
	if not db:
		print "Error while reaching DB."
		return False
	try:
		with db:
			# update database
			db.execute('''
		    	UPDATE Dictionary SET {0} = ? WHERE use_case = ? AND languageID = 
		    	(SELECT id from Languages where language = ?)
		    '''.format(values['<attribute>']), 
		    	(values['data'], 
		    	values['<use_case>'],
		    	values['<language>']))
	except sqlite3.Error as error:
		print "A database error has occured: ", error
		return False
	return True
	

def add_content(values, lang_name):
	"""Adds content to the database.

	"""
	
	db = setup_database() 

	if not db:
		print "Error while reaching DB."
		return False
	try:
		with db:
			
			#add language to lang db if not exists
			db.execute('''
			INSERT OR IGNORE INTO Languages (language) VALUES (?)
			''', (lang_name, ))
			
			for new_row in values:
				db.execute('''
			    	INSERT or REPLACE into Dictionary 
			    	(languageID, use_case, command, comment, links)
			    	VALUES((SELECT id from Languages where language = ?), ?, ?, ?, ?)
				''', (lang_name, 
					 new_row[0],
					 new_row[1],
					 new_row[2],
					 new_row[3]))
			return True
	except sqlite3.Error as error:
		print "A database error has occured: ", error
		return False
	return True		


def retrieve_content(location, selection_type):
	"""Retrieves command, comment from the DB.
	   Returns: List of tuples OR False
	"""
	
	db = setup_database()
	
	if not db:
		return False


	db_selection = select_from_db(db, location, selection_type)
	if not selection_type == "code":	
		selection_result = selected_rows_to_list(db_selection)
	else:
		selection_result = db_selection.fetchone()
	return selection_result # returns False if no rows were selected			


def select_from_db(db, location, selection_type):
	"""Selects from DB.
	   Returns: DB cursor Object or False

	"""
	
	if not selection_type in ('extended', 'language', 'basic', 'code', 'full'):
		print "DB received no valid selection type."
		return False

	try:
		with db:
		
			if selection_type == "extended":
		
				selection = db.execute('''
				    SELECT use_case, command, comment, code FROM Dictionary WHERE use_case LIKE ? AND languageID = 
			    	(SELECT id from Languages where language = ?) 
			    ''', (location['<use_case>']+'%', location['<language>']))
			

			elif selection_type	== "basic":
		
				selection = db.execute('''
				    SELECT use_case, command, code FROM Dictionary WHERE use_case LIKE ? AND languageID = 
				    (SELECT id from Languages where language = ?) 
			    ''', (location['<use_case>']+'%', location['<language>']))


			elif selection_type == "language":

				selection = db.execute('''
			    	SELECT use_case, command, code FROM Dictionary WHERE languageID = 
			    	(SELECT id from Languages where language = ?) 
			    ''', (location['<language>'], ))


			elif selection_type == "code":

				selection = db.execute('''
				    SELECT code FROM Dictionary WHERE use_case = ? and languageID = 
			    	(SELECT id from Languages where language = ?)
				    ''', (location['<use_case>'], location['<language>']))


			elif selection_type == "full":

				selection = db.execute('''
				    SELECT use_case, command, comment, links, code FROM Dictionary WHERE use_case LIKE ? AND languageID = 
				    (SELECT id from Languages where language = ?) 
				''', (location['<use_case>']+'%', location['<language>']))

	except sqlite3.Error as error:
		print "A database error has occured: ", error
		return False
	
	return selection


def selected_rows_to_list(all_rows):
	"""Packs all results from a SELECT statement into a list of tuples which contain
	   the field values of the rows.
	   Returns: list of tuples OR False	
	"""

	result_list = []
	for count, row in enumerate(all_rows):
		result_list.append((count+1, )+ row)
	if result_list:
		return result_list
	else:
		return False

