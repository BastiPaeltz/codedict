"""Defines the data processing / handling using local sqlite3 database.

 
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
		self._db_instance = establish_db_connection(self.db_path)
		self._setup_database()


	def _setup_database(self):
		"""Sets up the database for usage. Exits if connecting to DB or setting up
		tables fails.
		"""
		
		if not self._db_instance:
			print "Error while reaching DB."
			sys.exit(1) 
		
		if not self._create_tables():
			print "Error while creating DB tables."
			sys.exit(1)

 
	def _create_tables(self):
		"""Creates tables 'dictionary', 'languages', 'links' and 'config' if they not exist.

		"""

		try:
			with self._db_instance:
				# create tables
				self._db_instance.execute('''
			    	CREATE table IF NOT EXISTS Languages (id INTEGER PRIMARY KEY, 
			    		language TEXT, suffix TEXT)
				''')

				self._db_instance.execute('''
			    	CREATE table IF NOT EXISTS Dictionary 
			    	(id INTEGER PRIMARY KEY, languageID INTEGER, 
			    		problem TEXT, solution TEXT, comment TEXT, linkID INTEGER, code TEXT)
				''')

				self._db_instance.execute('''
			    	CREATE table IF NOT EXISTS Config (configItem TEXT PRIMARY KEY, value TEXT)
				''')

				self._db_instance.execute('''
					CREATE table IF NOT EXISTS Links (name TEXT PRIMARY KEY, 
					URL text, description TEXT, language TEXT)
				''')

				return True

		except sqlite3.Error as error:
			print "A database error has occured: ", error
			return False


	def get_config_item(self, config_item):
		"""Gets a config item (editor or line-length) from the Config table.

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
		"""Sets the editor row in the Config table of the DB.

		"""

		try:
			with self._db_instance:

				self._db_instance.execute('''
					INSERT or IGNORE INTO Config (configItem, value) VALUES (?, ?)
				''', (config_item, value, ))

				self._db_instance.execute('''
					UPDATE Config SET value = ? WHERE configItem = ?
				''', (value, config_item, ))
			
		except sqlite3.Error as error:
			print "A database error has occured: ", error
			sys.exit(1)

	def retrieve_suffix(self, lang_name):
		"""Retrieves suffix for 1 language from Language table of the DB. 

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


	def delete_content(self, values):
		"""Deletes content from the Dictionary table, language and problem field 
		have to match the rows values.
		"""

		try:
			with self._db_instance:
				
				self._db_instance.execute('''
			    	DELETE from Dictionary WHERE problem = ? AND languageID = 
			    	(SELECT id from Languages where language = ?)
			    ''', (values['problem'], values['language']))
			    
		except sqlite3.Error as error:
			print "A database error has occured: ", error
			sys.exit(1)


	def update_content(self, values):
		"""Updates content of the DB, not insert! Only for values whcih already exist.
		"""	

		try:
			with self._db_instance:
				# update database

				if values['attribute'] != 'link':
					self._db_instance.execute('''
			    	UPDATE Dictionary SET {0} = ? WHERE problem = ? AND languageID = 
			    	(SELECT id from Languages where language = ?)
			    	'''.format(values['attribute']), 
					(values['data'], 
					values['problem'],
					values['language']))
				else:
					self._db_instance.execute('''
			    	UPDATE Links SET {0} = ? WHERE problem = ? AND languageID = 
			    	(SELECT id from Languages where language = ?)
			    	'''.format(values['attribute']), 
			    	(values['data'], 
			    	values['problem'],
			    	values['language']))


		except sqlite3.Error as error:
			print "A database error has occured: ", error
			sys.exit(1)

### LINKS

	def upsert_links(self, values, operation_type='add'):
		"""Upserts (insert or update if exists) links into Link table.

		"""

		try:
			with self._db_instance:


				#add link to Links db if not exists
				self._db_instance.execute('''
				INSERT OR IGNORE INTO Links (name, url, language) VALUES (?, ?, ?)
				''', (values['link_name'], values['url'], values['language']))
				
				if operation_type == 'upsert':
				
					self._db_instance.execute('''
					UPDATE Links SET language = ? WHERE name = ? AND url = ?
					''', (values['language'], values['link_name'], values['url']))
				
		except sqlite3.Error as error:
			print "A database error has occured: ", error
			sys.exit(1)


	def delete_links(self, values):
		"""Deletes links from Link table.

		"""

		try:
			with self._db_instance:
				print values	
				self._db_instance.execute('''
			    	DELETE from Links WHERE url = ? 
			    ''', (values['url'], ))
			    
		except sqlite3.Error as error:
			print "A database error has occured: ", error
			sys.exit(1)


	def retrieve_links(self, values, selection_type):
		"""Retrieves links into Link table.

		"""
		try:
			with self._db_instance:
				if selection_type == 'open':

					selection = self._db_instance.execute('''
					SELECT url from Links WHERE name LIKE ? 
					''', (values['link_name']+'%', )) 
					return selection.fetchone()

				else: # display 
					if selection_type == 'display':
						selection = self._db_instance.execute('''
						SELECT name, url from Links WHERE name LIKE ?
						''', (values['link_name']+'%', )) 

					elif selection_type == 'lang_display': # lang display
						selection = self._db_instance.execute('''
						SELECT name, url, language from Links WHERE name LIKE ?
						AND language = ? 
						''', (values['link_name']+'%', values['language']))
						 
					else: # entire display
						selection = self._db_instance.execute('''
						SELECT name, url, language, description from Links WHERE name LIKE ?
						AND language = ? 
						''', (values['link_name']+'%', values['language'])) 

					selection_list = selected_rows_to_list(selection)
					return selection_list

		except sqlite3.Error as error:
			print "A database error has occured: ", error
			sys.exit(1)


	def upsert_code(self, values):
		"""Upserts (insert or update if exists) code into the DB. 
		"""

		try:
			with self._db_instance:


				#add language to lang db if not exists
				self._db_instance.execute('''
				INSERT OR IGNORE INTO Languages (language, suffix) VALUES (?, "")
				''', (values['language'], ))
				
				self._db_instance.execute('''
					UPDATE Dictionary SET code = ? WHERE problem = ? AND languageID = 
					(SELECT id from Languages where language = ?)
					''', (values['data'], 
					values['problem'],
					values['language']))
				
				self._db_instance.execute('''
						INSERT or IGNORE into Dictionary (id, languageID, problem, solution, comment, code)
				    	VALUES((SELECT id from Dictionary where problem = ? AND languageID = 
				    		(SELECT id from Languages where language = ?)) 
				    		,(SELECT id from Languages where language = ?), ?, '', '', ?)
				''', (values['problem'],
					values['language'], 
					values['language'], 
					values['problem'], 
					values['data']))

		except sqlite3.Error as error:
			print "A database error has occured: ", error
			sys.exit(1)


	def add_content(self, values, lang_name):
		"""Adds content to the database. Tries to insert and updates if 
		row already exists.
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
				    	(id, languageID, problem, solution, comment, code)
				    	VALUES((SELECT id from Dictionary where problem = ? AND languageID = 
				    		(SELECT id from Languages where language = ?)), 
				    		(SELECT id from Languages where language = ?), ?, ?, ?,
				    		COALESCE((SELECT code from Dictionary where problem = ? AND languageID = 
				    		(SELECT id from Languages where language = ?)), ''))
					''', (new_row[0], lang_name, lang_name, new_row[0], 
						new_row[1], new_row[2], new_row[0], lang_name))

		except sqlite3.Error as error:
			print "A database error has occured: ", error
			sys.exit(1)


	def retrieve_content(self, location, selection_type):
		"""Retrieves content, packs them in indexed tuples if needed
		and sends results back to calling function.
		"""
		
		db_selection = self._select_from_db(location, selection_type)
		if not selection_type == "code":	
			selection_result = selected_rows_to_list(db_selection)
		else:
			selection_result = db_selection.fetchone()
		return selection_result 		# returns False if no rows were selected			


	def _select_from_db(self, location, selection_type):
		"""Selects from DB. Runs correct query.

		"""
		
		if not selection_type in ('language', 'basic', 'code', 'full'):
			print "DB received no valid selection type."
			sys.exit(1)

		try:
			with self._db_instance:
			
				if selection_type == "basic":
			
					selection = self._db_instance.execute('''
					    SELECT problem, solution, code FROM Dictionary WHERE problem LIKE ? AND languageID = 
					    (SELECT id from Languages where language = ?) 
				    ''', (location['problem']+'%', location['language']))


				elif selection_type == "language":

					selection = self._db_instance.execute('''
				    	SELECT problem, solution, code FROM Dictionary WHERE languageID = 
				    	(SELECT id from Languages where language = ?) 
				    ''', (location['language'], ))


				elif selection_type == "code":

					selection = self._db_instance.execute('''
					    SELECT code FROM Dictionary WHERE problem = ? and languageID = 
				    	(SELECT id from Languages where language = ?)
					    ''', (location['problem'], location['language']))


				elif selection_type == "full":

					selection = self._db_instance.execute('''
					    SELECT problem, solution, comment, link, code FROM Dictionary WHERE problem LIKE ? AND languageID = 
					    (SELECT id from Languages where language = ?) 
					''', (location['problem']+'%', location['language']))

				return selection

		except sqlite3.Error as error:
			print "A database error has occured: ", error
			sys.exit(1)
		

def selected_rows_to_list(all_rows):
	"""Packs all results from a SELECT statement into a list of tuples 
	with index attached (at first position).	
	"""

	result_list = []
	for count, row in enumerate(all_rows):
		
		print row
		result_list.append((count+1, )+ row)
	if result_list:
		return result_list
	else:
		return False


def determine_db_path():
	"""Determines where the DB file is located. If executable is frozen the location 
	differentiates.
	"""

	if getattr(sys, 'frozen', False):
	       # The application is frozen
	    datadir = os.path.dirname(sys.executable)
	else:
	    # The application is not frozen
	    datadir = os.path.dirname(__file__)

	return datadir+'/res/codedict_db.DB'


def establish_db_connection(db_path):
	"""Establishes the connection to the DB.

	"""

	try:
		return sqlite3.connect(db_path)
		
	except sqlite3.Error as error:
		print "A database error has occured: ", error
		return False
