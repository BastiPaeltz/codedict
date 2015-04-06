"""processes the command line args.

"""

#relative import
import database as db  
import prettytable

#import from standard library
import tempfile
import re
import subprocess
import textwrap
import sys
import os
import urlparse
import webbrowser

###GENERAL ###


def start_process(cmd_line_args):
	"""Starts processing the command line args. 
	   Filters out unrelevant arguments.
	"""

	relevant_args = ({key: value for key, value in cmd_line_args.iteritems() 
					if value is not False and value is not None})

	print relevant_args
	if '--editor' in relevant_args:
		set_editor(relevant_args['editor'])

	elif '--suffix' in relevant_args:
		set_suffix(relevant_args['suffix'], relevant_args['language'])

	elif '--line' in relevant_args:
		set_line_length(relevant_args['integer'])

	elif '--wait' in relevant_args:
		del relevant_args['--wait']
		set_wait_option(relevant_args)

	else:
		body, flags = split_arguments(relevant_args)
		determine_proceeding(body, flags)


def set_wait_option(option):
	"""Sets the wait option to either on or off.

	"""

	if 'on' in option:
		value = "on"
		print "Enabling 'wait' option."
	else:
		value = ""
		print "Disabling 'wait' option."

	database = db.Database()
	database.set_config_item('wait', value)


def set_editor(editor):
	"""Sets the editor.

	"""

	database = db.Database()
	database.set_config_item('editor', unicode(editor.strip(), 'utf-8'))
	print "Setting editor {0} successfull.".format(editor)


def set_suffix(suffix, language):
	"""Sets the suffix.

	"""

	database = db.Database()	
	database.set_suffix(language.strip(), unicode(suffix, 'utf-8'))
	print "Setting suffix {0} for {1} successfull.".format(suffix, language)


def set_line_length(length):
	"""Sets the console's line length.

	"""

	try:
		int(length)
		database = db.Database()
		database.set_config_item('linelength', unicode(length.strip(), 'utf-8'))
		print "Setting your console line length to {0} successfull.".format(length)
	except ValueError:
		print "Console line length must be an integer."

def split_arguments(arguments):
	"""Splits the given arguments from the command line in content and flags.

	"""

	request, flags = {}, {}
	for key, item in arguments.iteritems(): 
		if key in ('-e', '-c', '-l', '-a', '-d', '-f', 
			'--code', '--cut', '--hline', '--suffix', '--display', '--open'):
			flags[key] = item
		else:
			request[key.lower()] = item 

	return (request, flags)


def determine_proceeding(body, flags):
	""" Checks which operation (add, display, ...)
		needs to be handled. 
	"""


	if '-f' in flags:
		process_file_adding(body, flags)
	elif '-d' in flags:
		determine_display_operation(body, flags)
	elif '-a' in flags:
		process_add_content(body, flags)
	elif '-c' in flags:
		process_code_adding(body)
	elif '-l' in flags:
		process_links(body, flags)
	else:
		print "An unexpected error has occured while processing {0} with options {1}".format(body, flags)


def check_for_suffix(language, database):
	"""Checks if the DB has a suffix for the requested language, if not 
	   it prompts to specify one.
	"""

	suffix = database.retrieve_suffix(language)

	if suffix:
		return suffix
	else:
		input_suffix = raw_input("Enter file suffix for language " +language+" : ").strip()
		database.set_suffix(language, input_suffix)
		return input_suffix


###OUTPUT ###

def check_for_editor(database):
	"""Checks for editor in the Database.

	"""

	editor_unicode = database.get_config_item('editor')

	if not editor_unicode:
		valid_input = False
		while not valid_input:
			try:
				editor_value = unicode(raw_input("Enter your editor: ").strip(), 'utf-8')
				valid_input = True
			except UnicodeError as error:
				print error
		database.set_config_item('editor', editor_value)
		editor_value = editor_value.encode('utf-8')
	else:
		editor_value = editor_unicode[0].encode('utf-8')

	return editor_value


def print_to_editor(table, database):
	"""Sets up a nice input form (editor) for viewing a large amount of content. -> Read only

	"""

	editor_value = check_for_editor(database)

	editor_list = [argument for argument in editor_value.split(" ")]

	prewritten_data = table.get_string() # prettytable to string

	with tempfile.NamedTemporaryFile(delete=False) as tmpfile:

		try:
			tmpfile.write(prewritten_data)
			tmpfile.flush()
			try:
		  		subprocess.Popen(editor_list + [tmpfile.name])
		  	except (OSError, IOError) as error:
		  		print "Error calling your editor - ({0}): {1}".format(error.errno, error.strerror)
		  		sys.exit(1)

		except (OSError, IOError) as error:
			print error
			sys.exit(1)
	return tmpfile


def process_printing(table, database):
	"""Processes all priting to console or editor.

	"""

	decision = decide_where_to_print(table)
	if decision == 'console':
		print table
		return False
	else:
		return print_to_editor(table, database) 


def decide_where_to_print(table):	
	"""Decides where to print to.

	"""

	if len(table.get_string().splitlines()) < 25:
		return 'console'
	else:
		valid_input = False
		while not valid_input:
			choice = raw_input(("Output longer than 25 lines - print to console anyway? (y/n) ")
				).strip().split(" ")[0]
			if choice in ('y', 'yes', 'Yes', 'Y'):
				valid_input = True
				return "console"
			elif choice in ('n', 'no', 'No', 'N'):
				valid_input = True
				return "editor"
			else:
				continue


def code_input_from_editor(suffix, database, existing_code):
	"""Sets up a nice input form (editor) for code adding and viewing.

	"""

	editor_value = check_for_editor(database)

	editor_list = [argument for argument in editor_value.split(" ")]

	prewritten_data = existing_code.encode('utf-8')

	try:
		wait_enabled = database.get_config_item('wait')
	except IndexError:
		wait_enabled = False

	with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmpfile:
		if existing_code:
			tmpfile.write(prewritten_data)
			tmpfile.seek(0)

		file_name = tmpfile.name

		if sys.platform == "win32" or wait_enabled: # windows or wait enabled 
			try:
	  			subprocess.Popen(editor_list + [tmpfile.name])
	  		except (OSError, IOError, ValueError) as error:
	  			print "Error calling your editor - ({0}): {1}".format(error.errno, error.strerror)
	  			sys.exit(1)

			tmpfile.close()

			valid_input = False
			while not valid_input:
			 	if raw_input("Are you done adding code? (y/n): ") != 'n':
			 		valid_input = True
			 	else:
			 		continue
		else: 	# platform != windows
			try:
	  			subprocess.call(editor_list + [tmpfile.name])
	  		except (OSError, IOError) as error:
	  			print "Error calling your editor - ({0}): {1}".format(error.errno, error.strerror)
	  			sys.exit(1)

	  	# no matter what platform from now on
		with open(file_name) as my_file:
			try:
				file_output = my_file.read()
			except (IOError, OSError) as error:
				print error
				sys.exit(1)
			except:
				print "An unexpected error has occured."
				sys.exit(1)

		try:
			os.remove(file_name)
		except OSError:
			print "Couldn't delete temporary file."

		return file_output


###CODE ###

def process_code_adding(body, database=False, code_of_target=False):
	"""Processes code adding, provides a nice input form for the user.

	"""

	if not database:
		database = db.Database()

	# If code isn't already retrieved (code_of_target), retrieve from DB. 
	if not code_of_target:
		existing_code = database.retrieve_content(body, "code")
		if not existing_code:
			existing_code = ""
		else:
			existing_code = existing_code[0] 	  
	else:
		existing_code = code_of_target

	suffix = check_for_suffix(body['language'], database)
	body['data'] = code_input_from_editor(suffix, database, existing_code)

	try:
		body['data'] = unicode(body['data'], 'utf-8')
	except UnicodeError as error:
		print error

	if body['data'] == existing_code:
		print "Nothing changed."		
	else:
		body['attribute'] = "code"
		database.upsert_code(body) 

	print "Finished - updated your codedict successfully."


###FILE ###

def process_file_adding(body, flags):
	"""Processes adding content to DB from a file.

	"""


	try:
		with open(body['path-to-file']) as input_file:
			file_text = input_file.read()
			input_file.close()
	except (OSError, IOError) as error:
		print "File Error({0}): {1}".format(error.errno, error.strerror)
		sys.exit(1)

	database = db.Database()

	if '--code' in flags:
		body['data'] = file_text
		database.upsert_code(body)	
	else:
		all_matches = (re.findall(r'%[^\|%]*?\|([^\|]*)\|[^\|%]*?\|([^\|]*)\|[^\|%]*\|([^\|]*)\|', 
		file_text, re.UNICODE))
		print all_matches
		database.add_content(all_matches, body['language'])
 	print "Finished - updated your codedict successfully."

	
###ADD ###

def process_links(body, flags):
	"""Processes link to codedict.

	"""
	# add links
	if not '--open' in flags and not '--display' in flags:

		if not 'link_name' in body:
			# set name based on url scheme 
			try:
				entire_url = urlparse.urlsplit(body['url'])
			except Error as e: # can this actually happen?
				print "This is not a valid url. \n", e
				sys.exit(1)
			for url_part in reversed(entire_url):
				if url_part:
					subpart = url_part.split("/")
					link_name = subpart[len(subpart)-1].replace('.html', '')
					break
			body['link_name'] = link_name
		database = db.Database()
		database.upsert_links(body)
		print "Added link to database."
	
	# display links	
	elif '--display' in flags:
		determine_display_operation(body, flags)

	# open link
	else:
		database = db.Database()
		db_result = database.retrieve_links(body, 'open')
		if db_result[0]:
			requested_url = db_result[0]
		else:
			print "No links found."
			sys.exit(0)
		if not requested_url.startswith('http'):
			requested_url = 'http://'+requested_url
		run_webbrowser(requested_url)

def run_webbrowser(url):
	"""Runs the url in the webbrowser.

	"""
	
	print "Opening your browser"
	os.close(2)
	os.close(1)
	os.open(os.devnull, os.O_RDWR)
	webbrowser.get().open(url)

def process_add_content(body, flags):
	"""Processes content adding. 

	"""

	if '-I' in flags or '-i' in flags:
		update_content(body)
	else:
		insert_content()


def update_content(body, database=False):
	"""Processes how to update content.

	"""
	if not database:
		database = db.Database()

	if body['attribute'] != 'del': 
		valid_input = False
		while not valid_input:
			try:
				body['data'] = unicode(raw_input("Change "+body['attribute']+" to: ").strip(), 'utf-8')
				valid_input = True
			except UnicodeError as error:
				print error
		database.update_content(body)		
	else:
		database.delete_content(body)


def insert_content():
	"""Processes how to insert content.

	"""

	content_to_add = {}

	valid_input = False
	while not valid_input:
		try:
			language = unicode(raw_input("Enter language: ").strip(), 'utf-8')
			valid_input = True
		except UnicodeError as error:
			print error

	for index, item in enumerate(('problem: ', 'solution: ', 'comment: ')):
		valid_input = False
		while not valid_input:
			try: 
				content_to_add[index] = unicode(raw_input("Enter "+ item).strip(), 'utf-8') 
				valid_input = True
			except UnicodeError as error:
				print error

	database = db.Database()
	database.add_content([content_to_add], language) # db method works best with lists
	print "Finished - updated your codedict successfully."


### DISPLAYING ###
 
def build_args_dict(body, flags):
	"""Determines and sets hline and cutsearch as well as links"""

	args_dict = {}	
	if '--cut' in flags and 'problem' in body:
		args_dict['cut_search'] = body['problem']
	elif '--cut' in flags and 'link_name' in body:
		args_dict['cut_search'] = body['link_name']
	else:
		args_dict['cut_search'] = False

	if '--hline' in flags:
		args_dict['hline'] = True 
	else:
		args_dict['hline'] = False

	if '-l' in flags:
		args_dict['link'] = True

	return args_dict


def determine_display_operation(body, flags):
	"""Processes display actions, checks if a nice form has to be provided or not.

	"""

	
	args_dict = determine_hline_and_cutsearch(body, flags)

	database = db.Database()

	display_type = "display"

	if '-l' in flags:
		display_type = "link"

		if '-e' in flags:
			results = database.retrieve_links(body, 'entire-display')			
			column_list = ["index", "link name", "url", "language", 'description']

		elif not 'language' in body:
			results = database.retrieve_links(body, 'display')
			column_list = ["index", "link name", "url"]
		
		else:
			results = database.retrieve_links(body, 'lang-display')			
			column_list = ["index", "link name", "url", "language"]

	elif '-e' in flags:
		if not 'problem' in body:
			body['problem'] = ""
		results = database.retrieve_content(body, "full")
		column_list = ["index", "problem", "solution", "comment", "code added?"]
	
	elif not 'problem' in body:
		results = database.retrieve_content(body, "language")
		column_list = ["index", "problem", "solution", "code added?"]
	
	else:
		results = database.retrieve_content(body, "basic")
		column_list = ["index", "problem", "solution", "code added?"]
	

	if results:

		console_linelength = set_console_length(database) 

		updated_results, table = build_table(column_list, results, console_linelength, args_dict)
		tmpfile = process_printing(table, database)  # tmpfile gets returned so it can be removed from os.
		
		state = State_Before_Follow_Up(database, body, flags, updated_results)
		state.process_follow_up_operation(display_type, tmpfile)
		state.perform_riginal_request(body, flags)
	else:
		print "No results."
		

def set_console_length(database):
	"""Gets console length from DB and sets it appropiately.

	"""

	console_linelength = database.get_config_item('linelength')
	if not console_linelength:
		console_linelength = 80
	else:
		console_linelength = int(console_linelength[0])
	return console_linelength


def build_table(column_list, all_rows, line_length, args_dict):
	"""Builds table and prints it to console.

	"""

	#column list length(-1)
	cl_length = len(column_list)-1
	
	result_table = prettytable.PrettyTable(column_list)
	if 'hline' in args_dict:
		result_table.hrules = prettytable.ALL 

	all_rows_as_list = []

	field_length = line_length/(cl_length+1)

	for row in all_rows:
		single_row = list(row)			# row is a tuple and contains db query results.
		for index in range(1, cl_length): 	# code and index dont need to be filled
			if 'cut_search' in args_dict and index == 1:
				single_row[index] = single_row[index].replace(args_dict['cut_search'], "", 1) 
			if not single_row[index]:
				single_row[index] = ""

			dedented_item = textwrap.dedent(single_row[index]).strip()
			single_row[index] = textwrap.fill(dedented_item, width=field_length)	

		#if code is present, print "yes", else "no"	
		if 'links' in args_dict and single_row[cl_length]:
			single_row[cl_length] = "yes"
		else:
			single_row[cl_length] = "no" 

		#add modified row to table, add original row to return-list
		result_table.add_row(single_row)
		all_rows_as_list.append(list(row))
	return (all_rows_as_list, result_table)


###FOLLOW UP ###

class State_Before_Follow_Up(object):
	"""State (table, query results, database etc.) after the initial 'query' gets saved.
	    Used for displaying operations only.

	"""

	def __init__(self, database, body, flags, query_result):
		self._database = database
		self._results = query_result
		self._original_body = body
		self._original_flags = flags

	def _prompt_by_index(self, prompt, default_attribute, tmpfile=False):
		"Prompts the user for further commands after displaying content or links."


		valid_input = False 
		while not valid_input:

			# clean up of previously created tempfile
			user_input = raw_input(prompt).strip().split(None, 1)
			
			if tmpfile:
				try:
					os.remove(tmpfile.name)
					tmpfile = False
				except OSError as error:
					print error 
					print "This error is not crucial for the program itself."

			# abort with 'enter' 		
			if not user_input:
				sys.exit(0)
			index = user_input[0]
			try:
				attribute = user_input[1].lower()
			except IndexError:
				attribute = default_attribute


			if (len(user_input) <= 2 and index.isdigit() 
									and int(index) >= 1 
									and int(index) <= len(self._results)):	

				actual_index = int(index)-1
				if attribute and attribute in ('problem', 'solution', 'comment', 'link', 'code', 'bind', 'del'):
					valid_input = True
				else:
					print "Wrong attribute, Please try again."
					valid_input = False
			else:
				print "Wrong index, Please try again."
		return (self._results[actual_index], attribute) 		


	def perform_original_request(self, body, flags):
		"""Performs original request again.

		"""

		return determine_proceeding(body, flags)

	def process_follow_up_operation(self, operation_type, tmpfile):
		"""Processes the 2nd operation of the user, e.g. code adding.

		"""

		# link table
		if operation_type == 'link':
			prompt = "Do you want to do more? Valid input: INDEX [('DEL' | 'BIND')] - Press ENTER to abort: \n"
			target, attribute = self._prompt_by_index(prompt, 'link', tmpfile)
			self._link_determine_operation(target, attribute)

		# dict table
		else:
			prompt = "Do you want to do more? Valid input: INDEX [ATTRIBUTE] - Press ENTER to abort: \n"
			target, attribute = self._prompt_by_index(prompt, 'code', tmpfile)
		
			self._original_body['problem'] = target[1]
			
			if attribute != 'code':
				self._original_body['attribute'] = attribute
				return update_content(self._original_body, database=self._database) 
			else:
				code_of_target = target[len(target)-1]
				if not code_of_target:
					code_of_target = " "
				return process_code_adding(self._original_body, code_of_target=code_of_target, database=self._database)


	def _link_determine_operation(self, target, attribute):
		"""Determines what operation to do on link table

		"""

		if attribute == 'link':
			self._original_body['link_name'] = target[1]
			link_url = self._database.retrieve_link(self._original_body, 'open')
			print link_url
			if link_url:
				requested_url = link_url[0]
				if not requested_url.startswith('http'):
					requested_url = "http://"+requested_url

				run_webbrowser(requested_url)
			else:
				print "No links."
				sys.exit(0)

		elif attribute == 'del':
			self._original_body['url'] = target[2] 
			self._database.delete_links(self._original_body)
			print "Deleting link {0} successfully.".format(target[1])

		elif attribute == 'bind':
			self._original_body['language'] = raw_input("Bind " +target[1]+" to language : ").strip()
			self._original_body['link_name'] = target[1]
			self._original_body['url'] = target[2]
			self._database.upsert_links(self._original_body, operation_type='upsert')
			print "Binding link {0} successfull.".format(self._original_body['link_name'])
