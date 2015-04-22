"""processes the command line args.

"""

#relative import
import database as db  
import lib.prettytable as prettytable

#import from standard library
import tempfile
import re
import subprocess
import textwrap
import sys
import os
import urlparse
import webbrowser


##GENERAL 


def start_process(cmd_line_args):
	"""Starts processing the command line args. 
	   Filters out unrelevant arguments.
	"""

	relevant_args = ({key: value for key, value in cmd_line_args.iteritems() 
					if value is not False and value is not None})

	relevant_args = unicode_everything(relevant_args)

	if '--editor' in relevant_args:
		set_editor(relevant_args['EDITOR'])

	elif '--suffix' in relevant_args:
		set_suffix(relevant_args['SUFFIX'], relevant_args['LANGUAGE'])

	elif '--line' in relevant_args:
		set_line_length(relevant_args['INTEGER'])

	elif '--wait' in relevant_args:
		set_wait_option(relevant_args)

	else:
		body, flags = split_arguments(relevant_args)
		determine_proceeding(body, flags)


def set_wait_option(option):
	"""Sets the wait option to either on or off.

	"""

	value = ""
	if 'on' in option:
		value = "on"
		print "Enabling 'wait' option."
	else:
		print "Disabling 'wait' option."

	database = db.Database()
	database.set_config_item('wait', value)


def set_editor(editor):
	"""Sets the editor.

	"""

	database = db.Database()
	database.set_config_item('editor', editor.strip())
	print "Setting editor {0} successfull.".format(editor.encode('utf-8'))


def set_suffix(suffix, language):
	"""Sets the suffix for a specific language.

	"""

	database = db.Database()	
	database.set_suffix(language.strip(), suffix)
	print "Setting suffix {0} for {1} successfull.".format(suffix.encode('utf-8'), language.encode('utf-8'))


def set_line_length(length):
	"""Sets the console's line length.

	"""

	try:
		int(length)
		database = db.Database()
		database.set_config_item('linelength', length.encode('utf-8'))
		print "Setting your console line length to {0} successfull.".format(length)
	except ValueError:
		print "Console line length must be an integer."

def split_arguments(arguments):
	"""Splits the given arguments from the command line in content and flags.

	"""

	request, flags = {}, {}
	for key, item in arguments.iteritems(): 
		if key in ('-c', '-l', '-a', '-d', '-f', '-t', 
			'--hline', '--suffix', '--open'):
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
		insert_content()
	elif '-c' in flags:
		process_code_adding(body)
	elif '-l' in flags:
		process_links(body, flags)
	else:
		print "An unexpected error has occured"

def check_for_suffix(language, database):
	"""Checks if the DB has a suffix for the requested language, if not 
	   it prompts to specify one.
	"""

	suffix = database.retrieve_suffix(language)

	if suffix:
		return suffix
	else:
		input_suffix = process_and_validate_input("Enter file suffix for language " +language+" : ")
		database.set_suffix(language, input_suffix)
		return input_suffix


###OUTPUT ###

def check_for_editor(database):
	"""Checks for editor in the Database.

	"""

	editor_unicode = database.get_config_item('editor')

	if not editor_unicode:
		editor_value = process_and_validate_input("Enter your editor: ")
		database.set_config_item('editor', editor_value)
		editor_value = editor_value.encode('utf-8')
	else:
		editor_value = editor_unicode[0].encode('utf-8')

	return editor_value


def print_to_editor(table, database):
	"""Sets up a nice input form (editor) for viewing a large amount of content. -> Read only

	"""

	editor_value = check_for_editor(database)

	# subprocess works best with lists instead of strings
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
		tmpfile = False
	else:
		tmpfile = print_to_editor(table, database) 
	return tmpfile

def decide_where_to_print(table):	
	"""Decides where to print to.

	"""

	if len(table.get_string().splitlines()) < 25: # output smaller than 25 lines
		return 'console'

	else:
		
		decision = ""
		while decision == "":
			choice = process_and_validate_input("Output longer than 25 lines - print to console anyway? (y/n)")

			if choice in ('y', 'yes', 'Yes', 'Y'):
				decision = "console"
			elif choice in ('n', 'no', 'No', 'N'):
				decision = "editor"
			else:
				continue
		
		return decision		

def input_from_editor(database, existing_content="", suffix=""):
	"""Sets up a nice input form (editor) for code adding and viewing.

	"""

	editor_value = check_for_editor(database)

	editor_list = [argument for argument in editor_value.split(" ")]

	prewritten_data = existing_content.encode('utf-8')

	try:
		wait_enabled = database.get_config_item('wait')
	except IndexError:
		wait_enabled = False

	with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmpfile:
		if existing_content:
			tmpfile.write(prewritten_data)
			tmpfile.seek(0)

		file_name = tmpfile.name

		if sys.platform == "win32" or wait_enabled: # windows or wait enabled 
			
			# tmpfile is read after user is finished with editing, (tmpfile gets closed before)
			try:
				subprocess.Popen(editor_list + [tmpfile.name])
			except (OSError, IOError, ValueError) as error:
				print "Error calling your editor - ({0}): {1}".format(error.errno, error.strerror)
				sys.exit(1)

			tmpfile.close()

			go_ahead = False
			while not go_ahead:
			 	if process_and_validate_input("Are you done adding code? (y/n): ") == 'y':
			 		go_ahead = True
			 	else:
			 		continue
		else: 	# platform != windows
			try:
				subprocess.call(editor_list + [tmpfile.name])
			except (OSError, IOError) as error:
				print "Error calling your editor - ({0}): {1}".format(error.errno, error.strerror)
				sys.exit(1)

	# no matter what platform from now on
		return read_and_delete_tmpfile(file_name)


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
	body['data'] = input_from_editor(database, existing_content=existing_code, suffix=suffix)

	try:
		body['data'] = unicode(body['data'], 'utf-8')
	except UnicodeError as error:
		print error

	#determine if data needs to be written to the database
	if body['data'] == existing_code:
		print "Nothing changed."		
	else:
		body['attribute'] = "code"
		database.upsert_solution(body)

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

	# if file content should be treated as code, write it to DB. Otherwise find matches with regex.
	if '--code' in flags:
		body['data'] = file_text
		database.upsert_code(body)	
	else:
		all_matches = (re.findall(r'%[^\|%]*?\|([^\|]*)\|[^\|%]*?\|([^\|]*)\|[^\|%]*\|([^\|]*)\|', 
		file_text, re.UNICODE))
		database.add_content(all_matches, body['language'])
	print "Finished - updated your codedict successfully."

	
## LINKS

def process_links(body, flags):
	"""Processes link to codedict.

	"""
	# add links
	if '--open' not in flags and '--display' not in flags:
		if 'link_name' not in body:
			# set name based on url scheme 
				
			entire_url = urlparse.urlsplit(body['url'])
			for url_part in reversed(entire_url):
				if url_part:
					subpart = url_part.split("/")
					link_name = subpart[len(subpart)-1].replace('.html', '')
					break
			if not entire_url.scheme:
				body['link_name'] = "http://"+link_name
			else:
				body['link_name'] = link_name

		if 'language' not in body:
			body['original-lang'] = ""
			body['language'] = ""
		else:
			body['original-lang'] = body['language']
		database = db.Database()
		database.upsert_links(body)
		print "Added link {0} to database.".format(body['link_name'].encode('utf-8'))
		sys.exit(0)	

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
	# needed for surpressing error messages in console when opening browser
	os.close(2)
	os.close(1)
	os.open(os.devnull, os.O_RDWR)
	webbrowser.get().open(url)
	sys.exit(0)

## ADDING

def update_content(body, database=False):
	"""Processes how to update content.

	"""
	if not database:
		database = db.Database()

	if body['attribute'] != 'del': 
	
		if body['attribute'] != 'solution':
			body['data'] = process_and_validate_input("Change "+body['attribute']+" to: ")
			database.update_content(body)
		else:
			process_code_adding(body, database=database) 
	else:
		database.delete_content(body)


def insert_content():
	"""Processes how to insert content.

	"""

	content_to_add = {}
	
	# get valid input 
	database = db.Database()
	
	language = process_and_validate_input("Enter language: ")
	content_to_add[0] = process_and_validate_input("Enter your tags - seperated with ';' : ")
	content_to_add[1] = process_and_validate_input("Enter problem: ")

	# no editor wished
	if content_to_add[1].startswith('!!'):
		content_to_add[1] = content_to_add[1].replace('!!', '', 1)
		content_to_add[2] = process_and_validate_input("Enter solution: ")
	else:
		content_to_add[2] = input_from_editor(database) 
				
	database.add_content([content_to_add], language) # db method works best with lists
	print "Finished - updated your codedict successfully."


### DISPLAYING functions ###

def determine_display_operation(body, flags):
	"""Processes display actions, checks if a nice form has to be provided or not.

	"""

	print flags
	args_dict = build_args_dict(body, flags)

	database = db.Database()

	display_type = "display"

	results = []
 
	if '-t' in flags:
		display_type = "tag"
		results, column_list = get_dict_results(database, body, flags)

	elif '-l' in flags:
		display_type = "link"
		results, column_list = get_link_results(database, body, flags)
	
	else:
		results, column_list = get_dict_results(database, body, flags)

	if results:

		console_linelength = set_console_length(database) 

		updated_results, table = build_table(column_list, results, console_linelength, args_dict)
		tmpfile = process_printing(table, database)  # tmpfile gets returned so it can be removed from os.
		state = State(database, body, flags, updated_results)
		state.process_follow_up_operation(display_type, tmpfile)
		state.perform_original_request(body, flags)
	else:
		print "No results."

def get_link_results(database, body, flags):
	"""Gets all results for link query from DB and returns the column list additionally.

	"""

	# if '-t' in flags:
	# 	results = database.retrieve_links_per_tag(body)			
	# 	column_list = ["index", "link name", "url", "language"]

	if 'searchpattern' not in body:
		body['searchpattern'] = ""  
		results = database.retrieve_links(body, 'display')
		column_list = ["index", "link name", "url", "language"]
	
	else:
		results = database.retrieve_links(body, 'lang-display')			
		column_list = ["index", "link name", "url"]

	return (results, column_list)
		
def get_dict_results(database, body, flags):
	""" TODO

	"""

	if '-t' in flags:
		results = database.retrieve_dict_per_tags(body)			
		column_list = ["index", "problem", "solution"]

	# if '-e' in flags:
	# 	if 'searchpattern' not in body:
	# 		body['problem'] = ""
	# 	results = database.retrieve_content(body, "full")
	# 	column_list = ["index", "problem", "solution preview"]
	
	elif 'searchpattern' not in body:
		results = database.retrieve_content(body, "language")
		column_list = ["index", "problem", "solution preview"]
	
	else:
		results = database.retrieve_content(body, "basic")
		column_list = ["index", "language", "problem", "solution preview"]

	return (results, column_list)

def set_console_length(database):
	"""Gets console length from DB and sets it appropiately. --> convert to int

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
	print all_rows
	for row in all_rows:
		single_row = list(row)			# row is a tuple and contains db query results.
		
		if not 'link' in args_dict:
			if len(single_row[cl_length]) > 50:
				appended_string = "..."
			else:
				appended_string = ""
			single_row[cl_length] = single_row[cl_length][0:50] + appended_string 

		for index in range(1, cl_length+1): 	# code and index dont need to be filled
			if not single_row[index]:
				single_row[index] = ""

			dedented_item = textwrap.dedent(single_row[index]).strip()
			single_row[index] = textwrap.fill(dedented_item, width=field_length)	

		# print 2 lines of solution as preview
		#if code is present, print "yes", else "no"	
		# if 'links' not in args_dict and single_row[cl_length]:
		# 	single_row[cl_length] = "yes"
		# else:
		# 	single_row[cl_length] = "no" 

		#add modified row to table, add original row to return-list
		result_table.add_row(single_row)
		all_rows_as_list.append(list(row))
	return (all_rows_as_list, result_table)
	
###FOLLOW UP ###
	
class State(object):
	"""State (table, query results, database etc.) after the initial 'query' gets saved.
		Used for 'displaying' operations only.

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
			user_input = process_and_validate_input(prompt).split(None, 1)
			
			if tmpfile:
				try:
					os.remove(tmpfile.name)
					tmpfile = False
				except OSError as error:
					print error 
					print "This error is not crucial for the program itself - will continue."

			# abort with 'enter' 		
			if not user_input:
				sys.exit(0)
			index = user_input[0]
			try:
				attribute = user_input[1].lower()
			except IndexError:
				attribute = default_attribute


			if (len(user_input) <= 2 and index.isdigit() and 
			int(index) >= 1 and int(index) <= len(self._results)):	

				actual_index = int(index)-1
				if attribute and attribute in ('problem', 'solution', 'link', 'code', 'lang', 'del'):
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

		print "\n---------------\n"
		return determine_proceeding(body, flags)

	def process_follow_up_operation(self, operation_type, tmpfile):
		"""Processes the 2nd operation of the user, e.g. code adding.

		"""

		# link table
		if operation_type == 'link':
			prompt = "Do you want to do more? Valid input: INDEX [ACTION] - Press ENTER to abort: \n"
			target, attribute = self._prompt_by_index(prompt, 'link', tmpfile)
			self._link_determine_operation(target, attribute)

		# dict table
		else:
			prompt = "Do you want to do more? Valid input: INDEX [ACTION] - Press ENTER to abort: \n"
			target, attribute = self._prompt_by_index(prompt, 'code', tmpfile)
		
			self._original_body['problem'] = target[1]
			print self._original_body	
			if attribute != 'code':
				self._original_body['attribute'] = attribute
				return update_content(self._original_body, database=self._database) 
			else:
				code_of_target = target[len(target)-1]
				if not code_of_target:
					code_of_target = " "
				return process_code_adding(self._original_body, 
				code_of_target=code_of_target, database=self._database)


	def _link_determine_operation(self, target, attribute):
		"""Determines what operation to do on link table

		"""

		# default - run link in webbrowser
		if attribute == 'link':
			self._original_body['link_name'] = target[1]
			link_url = self._database.retrieve_links(self._original_body, 'open')
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
			print "Deleting link {0} successfully.".format(target[1].encode('utf-8'))

		# bind language to link
		elif attribute == 'lang':
			self._original_body['language'] = process_and_validate_input("Bind "+target[1]+" to language : ")
			self._original_body['link_name'] = target[1]
			self._original_body['url'] = target[2]
			self._original_body['original-lang'] = target[-1]
			self._database.upsert_links(self._original_body, operation_type='upsert')
			print "Binding link {0} successfull.".format(self._original_body['link_name'].encode('utf-8'))

		# set description for link
		else: 
			print "Error with flags."	

## HELPER

def process_and_validate_input(prompt):
	""" Processes trivial input and validates it. Returns the user's input.

	"""

	valid_input = False
	while not valid_input:
		try:
			user_input = unicode(raw_input(prompt).strip(), 'utf-8')
			valid_input = True
		except UnicodeError as error:
			print error
	return user_input 


def build_args_dict(body, flags):
	"""Determines and sets hline and cutsearch as well as links based 
	if they are present in flags / body. --> Is needed for building table.
	"""

	args_dict = {}	
	if '--cut' in flags and 'problem' in body:
		args_dict['cut_search'] = body['problem']
	elif '--cut' in flags and 'link_name' in body:
		args_dict['cut_search'] = body['link_name']

	if '--hline' in flags:
		args_dict['hline'] = True 

	if '-l' in flags:
		args_dict['link'] = True

	return args_dict


def unicode_everything(input_dict):
	"""Converts every value of the input_dict dict which contains strings into unicode.
 
	"""

	for key, value in input_dict.iteritems():
		if type(value) is str:
			try:
				input_dict[key] = unicode(value, 'utf-8')
			except UnicodeError as error:
				print error
				input_dict[key] = process_and_validate_input("Enter " + key + " again: ")
	return input_dict


def read_and_delete_tmpfile(file_name):
	"""Reads from tmpfile and tries to delete it afterwards.

	"""

	with open(file_name) as my_file:
			try:
				file_output = my_file.read()
			except (IOError, OSError) as error:
				print error
				sys.exit(1)

	try:
		os.remove(file_name)
	except OSError:
		print "Couldn't delete temporary file." 

	return file_output
