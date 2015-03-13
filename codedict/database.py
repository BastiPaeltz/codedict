"""Defines the data processing / handling using local sqlite3 database

 
"""

#import from standard library
import sqlite3
import sys
import os

class Database(object):
	"""DB class, handles all connections with the database.

	""" 

	def __init__(self):
		self.db_path = determine_db_path()
		print self.db_path
		self._db_instance = establish_db_connection(self.db_path)
		self._setup_database()


	def _setup_database(self):
		"""Sets up the database for usage.

		"""
		
		if not self._db_instance:
			print "Error while reaching DB."
			sys.exit(1) 
		
		if not self._create_table():
			print "Error while creating DB tables."
			sys.exit(1)

 
	def _create_table(self):
		"""Creates tables 'dictionary' and 'languages'.

		"""

		try:
			with self._db_instance:
				# create tables
				self._db_instance.execute('''
			    	CREATE table IF NOT EXISTS Languages (id INTEGER PRIMARY KEY, 
			    		language TEXT, suffix TEXT)
				''')

				self._db_instance.execute('''
			    	CREATE table IF NOT EXISTS Dictionary (id INTEGER PRIMARY KEY, languageID INTEGER, 
			    		usage TEXT, execution TEXT, comment TEXT, code TEXT)
				''')

				self._db_instance.execute('''
			    	CREATE table IF NOT EXISTS Config (id INTEGER PRIMARY KEY, configItem TEXT, value TEXT)
				''')
				return True
		except sqlite3.Error as error:
			print "A database error has occured: ", error
			return False


	def delete_content(self, values):
		"""Changes content of the database.

		"""

		try:
			with self._db_instance:
				
				self._db_instance.execute('''
			    	DELETE from Dictionary WHERE usage = ? AND languageID = 
			    	(SELECT id from Languages where language = ?)
			    ''', (values['USAGE'], values['LANGUAGE']))
			    
		except sqlite3.Error as error:
			print "A database error has occured: ", error
			sys.exit(1)


	def get_config_item(self, config_item):
		"""Gets a config item (editor or line-length).

		"""

		try:
			with self._db_instance:
				value = self._db_instance.execute('''
					SELECT value from Config where configItem = ?
				''', (config_item, ))

			return value.fetchone()
		except sqlite3.Error as error:
			print "A database error has occured: ", error
			sys.exit(1)


	def set_config_item(self, config_item, value):
		"""Sets the editor.

		"""

		try:
			with self._db_instance:

				self._db_instance.execute('''
					INSERT or IGNORE INTO Config (configItem, value) VALUES (?, ?)
				''', (config_item, value))

				self._db_instance.execute('''
					UPDATE Config SET value = ? WHERE configItem = ?
				''', (value, config_item))

		except sqlite3.Error as error:
			print "A database error has occured: ", error
			sys.exit(1)


	def retrieve_suffix(self, lang_name):
		"""Retrieves suffix for 1 language from DB

		"""

		try:
			with self._db_instance:

				suffix = self._db_instance.execute('''
				SELECT suffix from Languages where language = ?
				''', (lang_name, ))

			return suffix.fetchone()[0]
		except sqlite3.Error as error:
			print "A database error has occured: ", error
			sys.exit(1)


	def set_suffix(self, lang_name, suffix):
		"""Inserts suffix for 1 language into the DB.

		"""
 
		try:
			with self._db_instance:
				self._db_instance.execute('''
				UPDATE Languages SET suffix = ? WHERE language = ?
				''', (suffix, lang_name, ))

		except sqlite3.Error as error:
			print "A database error has occured: ", error
			sys.exit(1)


	def upsert_code(self, values):
		"""Changes content of the dictionary.
		   Returns: True or False
		"""

		try:
			with self._db_instance:

				self._db_instance.execute('''
					UPDATE Dictionary SET {0} = ? WHERE usage = ? AND languageID = 
					(SELECT id from Languages where language = ?)
					'''.format(values['attribute']), 
					(values['data'], 
					values['USAGE'],
					values['LANGUAGE']))
				
				self._db_instance.execute('''
						INSERT or IGNORE into Dictionary (id, languageID, usage, execution, comment, code)
				    	VALUES((SELECT id from Dictionary where usage = ? AND languageID = 
				    		(SELECT id from Languages where language = ?)) 
				    		,(SELECT id from Languages where language = ?), ?, '', '', ?)
				''', (values['USAGE'],
					values['LANGUAGE'], 
					values['LANGUAGE'], 
					values['USAGE'], 
					values['data']))

		except sqlite3.Error as error:
			print "A database error has occured: ", error
			sys.exit(1)
		

	def update_content(self, values):
		"""Changes content of the dictionary.
		   Returns: True or False
		"""	

		try:
			with self._db_instance:
				# update database
				self._db_instance.execute('''
		    	UPDATE Dictionary SET {0} = ? WHERE usage = ? AND languageID = 
		    	(SELECT id from Languages where language = ?)
		    	'''.format(values['attribute']), 
		    	(values['data'], 
		    	values['USAGE'],
		    	values['LANGUAGE']))

		except sqlite3.Error as error:
			print "A database error has occured: ", error
			sys.exit(1)


	def add_content(self, values, lang_name):
		"""Adds content to the database.

		"""
		
		try:
			with self._db_instance:
				
				#add language to lang db if not exists
				self._db_instance.execute('''
				INSERT OR IGNORE INTO Languages (language, suffix) VALUES (?, "")
				''', (lang_name, ))
				
				for new_row in values:
					self._db_instance.execute('''
				    	INSERT or REPLACE into Dictionary 
				    	(id, languageID, usage, execution, comment, code)
				    	VALUES((SELECT id from Dictionary where usage = ? AND languageID = 
				    		(SELECT id from Languages where language = ?)), 
				    		(SELECT id from Languages where language = ?), ?, ?, ?,
				    		COALESCE((SELECT code from Dictionary where usage = ? AND languageID = 
				    		(SELECT id from Languages where language = ?)), ''))
					''', (new_row[0], lang_name, lang_name, new_row[0], 
						new_row[1], new_row[2], new_row[0], lang_name))

		except sqlite3.Error as error:
			print "A database error has occured: ", error
			sys.exit(1)


	def retrieve_content(self, location, selection_type):
		"""Retrieves execution, comment from the DB.
		   Returns: List of tuples OR False
		"""
		
		db_selection = self._select_from_db(location, selection_type)
		if not selection_type == "code":	
			selection_result = selected_rows_to_list(db_selection)
		else:
			selection_result = db_selection.fetchone()
		return selection_result 		# returns False if no rows were selected			


	def _select_from_db(self, location, selection_type):
		"""Selects from DB.
		   Returns: DB cursor Object or False

		"""
		
		if not selection_type in ('language', 'basic', 'code', 'full'):
			print "DB received no valid selection type."
			sys.exit(1)

		try:
			with self._db_instance:
			
				if selection_type == "basic":
			
					selection = self._db_instance.execute('''
					    SELECT usage, execution, code FROM Dictionary WHERE usage LIKE ? AND languageID = 
					    (SELECT id from Languages where language = ?) 
				    ''', (location['USAGE']+'%', location['LANGUAGE']))


				elif selection_type == "language":

					selection = self._db_instance.execute('''
				    	SELECT usage, execution, code FROM Dictionary WHERE languageID = 
				    	(SELECT id from Languages where language = ?) 
				    ''', (location['LANGUAGE'], ))


				elif selection_type == "code":

					selection = self._db_instance.execute('''
					    SELECT code FROM Dictionary WHERE usage = ? and languageID = 
				    	(SELECT id from Languages where language = ?)
					    ''', (location['USAGE'], location['LANGUAGE']))


				elif selection_type == "full":

					selection = self._db_instance.execute('''
					    SELECT usage, execution, comment, code FROM Dictionary WHERE usage LIKE ? AND languageID = 
					    (SELECT id from Languages where language = ?) 
					''', (location['USAGE']+'%', location['LANGUAGE']))

				return selection

		except sqlite3.Error as error:
			print "A database error has occured: ", error
			sys.exit(1)
		


def selected_rows_to_list(all_rows):
	"""Packs all results from a SELECT statement into a list of tuples which contain
	   the field values of the rows.
	"""

	result_list = []
	for count, row in enumerate(all_rows):
		result_list.append((count+1, )+ row)
	if result_list:
		return result_list
	else:
		return False

def determine_db_path():
	"""Determines where the DB is located.

	"""
	#TODO: not ideal ...

	print os.path.dirname(__file__)
	if sys.platform == 'win32':
		return "data/codedict_db.DB"
	elif sys.platform == 'linux2':
		return os.path.dirname(__file__)+'/res/codedict_db.DB'
	else:
		print "Your system may not be supported as of yet."
		return "res/codedict_db.DB"


def establish_db_connection(db_path):
	"""Establishes the connection to the DB.
	   Returns: DB object or False
	"""

	try:
		return sqlite3.connect(db_path)
		
	except sqlite3.Error as error:
		print "A database error has occured: ", error
		return False
