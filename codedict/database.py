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
		db = sqlite3.connect('../res/codedict.DB')
	except sqlite3.DatabaseError:
		print "Database is encrypted or not a DB file."
		return False
		#todo create db in case of failure
	return db	


def setup_database(language):
	"""Sets up the database for SELECT usage.

	"""
	
	db = establish_db_connection()
	if not db:
		print "Error while reaching DB."
		return False
	
	if not check_for_table_existence(language, db):
		print "No such table"
		return False

	return db


def create_table(language):
	"""Creates a table for a specific language in the DB.
       Returns: True or False
	"""

	db = establish_db_connection()
	
	if not db:
		print "Error while reaching DB."
		return False
	try:
		with db:
			# create table
			db.execute('''
		    	CREATE table IF NOT EXISTS {0} (id INTEGER PRIMARY KEY, 
		    		use_case TEXT, command TEXT, comment TEXT, code TEXT)
			'''.format(language))
			print "Created table", language
	except:
		#TODO proper exception handling 
		print "Exception create tabkle"
		return False
	return True	


def check_for_table_existence(table_name, database):
	"""Checks if a table exists.

	"""
	db_execute = database.execute('''
		    SELECT name FROM sqlite_master WHERE type='table' AND name=?
		    ''', (table_name, ))
	return db_execute.fetchone()


def update_content(values):
	"""Changes content of the database.
	   Returns: True or False
	"""

	db = establish_db_connection() 
	
	if not db:
		print "Error while reaching DB."
		return False
	try:
		with db:
			# update database
			db.execute('''
		    	UPDATE {0} SET {1} = ? WHERE use_case = ?
		    '''.format(values['<language>'], 
		    	values['<attribute>']), 
		    	(values['data'], 
		    	values['<use_case>']))
	except sqlite3.IntegrityError:
		pass
	return True
	

def add_content(values, table_name):
	"""Adds content to the database.

	"""

	db = establish_db_connection()
	
	if not db:
		print "Error while reaching DB."
		return False
	try:
		with db:
			for new_row in values:
				rows = db.execute('''
			    	INSERT or REPLACE into {0} 
			    	(use_case, command, comment)
			    	VALUES(?, ?, ?)
				'''.format(table_name), 
					(fill(new_row[0], width=17), 
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
	
	db = setup_database(location['<language>'])
	
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
			    SELECT command, comment, code FROM {0} where use_case LIKE ?
			    '''.format(location['<language>']), (location['<use_case>']+'%',))
		

		elif selection_type	== "basic":
	
			selection = db.execute('''
		    SELECT ltrim(use_case, ?), command, code FROM {0} WHERE use_case LIKE ? 
		    '''.format(location['<language>']), 
		    (location['<use_case>'], location['<use_case>']+'%'))


		elif selection_type == "language":

			selection = db.execute('''
					    SELECT command, use_case, code FROM {0} 
					    '''.format(location['<language>']))


		elif selection_type == "code":

			selection = db.execute('''
			    SELECT code FROM {0} WHERE use_case = ? 
			    '''.format(location['<language>']), (location['<use_case>'],))


		elif selection_type == "full":

			selection = db.execute('''
		    SELECT use_case, command, comment, code FROM {0} WHERE use_case LIKE ?
		    '''.format(location['<language>']), (location['<use_case>']+'%',))

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
