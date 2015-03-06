"""Defines the data processing / handling using local sqlite3 database

 
"""

#import from standard library
import sqlite3
from textwrap import fill




def establish_db_connection():
	"""Establishes the connection to the DB.
	   Returns: DB object or False
	"""

	try:
		db = sqlite3.connect('../res/codedict0_4.DB')
	except sqlite3.DatabaseError:
		print "Database is encrypted or not a DB file."
		return False
		#todo create db in case of failure
	return db	


def setup_database():
	"""Sets up the database for usage.

	"""
	
	db = establish_db_connection()
	if not db:
		print "Error while reaching DB."
		return False
	
	if not create_table(db):
		return False
	return db


def create_table(db):
	"""Creates a table for a specific language in the DB.
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
		    	CREATE table IF NOT EXISTS Dictionary (id INTEGER PRIMARY KEY, 
		    		languageID INTEGER, use_case TEXT, command TEXT, comment TEXT, code TEXT)
			''')

			print "Created table language"
	except:
		#TODO proper exception handling 
		print "Exception create tabkle"
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
	except sqlite3.IntegrityError as e:
		print "error({0}): {1}".format(e.errno, e.strerror)
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
				rows = db.execute('''
			    	INSERT or REPLACE into Dictionary 
			    	(languageID, use_case, command, comment)
			    	VALUES((SELECT id from Languages where language = ?), ?, ?, ?)
				''', (lang_name, 
					 fill(new_row[0], width=17), 
				 	 fill(new_row[1], width=22), 
				 	 fill(new_row[2], width=22)))
				#TODO muss der output sein?
				for items in rows: 
					print "Row added: ", items	 
			return True
	except sqlite3.IntegrityError:
		#TODO: Proper exception handling
		print "Cant add element twice"
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
	print db_selection
	if not selection_type == "code":	
		selection_result = selected_rows_to_list(db_selection)
	else:
		selection_result = db_selection.fetchone()
		print selection_result
	return selection_result # returns False if no rows were selected			


def select_from_db(db, location, selection_type):
	"""Selects from DB.
	   Returns: DB cursor Object or False

	"""
	
	if not selection_type in ('extended', 'language', 'basic', 'code', 'full'):
		print "No valid selection type received"
		return False

	with db:
	
		if selection_type == "extended":
	
			selection = db.execute('''
			    SELECT ltrim(use_case, ?), command, comment code FROM Dictionary WHERE use_case LIKE ? AND languageID = 
		    	(SELECT id from Languages where language = ?) 
		    ''', (location['<use_case>'], location['<use_case>']+'%', location['<language>']))
		

		elif selection_type	== "basic":
	
			selection = db.execute('''
			    SELECT ltrim(use_case, ?), command, code FROM Dictionary WHERE use_case LIKE ? AND languageID = 
			    (SELECT id from Languages where language = ?) 
		    ''', (location['<use_case>'], location['<use_case>']+'%', location['<language>']))


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
			    SELECT ltrim(use_case, ?), command, code FROM Dictionary WHERE use_case LIKE ? AND languageID = 
			    (SELECT id from Languages where language = ?) 
			''', (location['<use_case>'], location['<use_case>']+'%', location['<language>']))

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
