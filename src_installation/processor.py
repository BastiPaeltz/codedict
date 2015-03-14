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

###GENERAL ###


def start_process(cmd_line_args):
	"""Starts processing the command line args. 
	   Filters out unrelevant arguments.
	"""

	relevant_args = ({key: value for key, value in cmd_line_args.iteritems() 
					if value is not False and value is not None})

	if '--editor' in relevant_args:
		database = db.Database()
		database.set_config_item('editor', unicode(relevant_args['EDITOR'].strip(), 'utf-8'))
		print "Setting editor {0} successfull.".format(relevant_args['EDITOR'])

	elif '--suffix' in relevant_args:
		database = db.Database()	
		database.set_suffix(relevant_args['LANGUAGE'].strip(), unicode(relevant_args['SUFFIX'], 'utf-8'))
		print "Setting suffix {0} for {1} successfull.".format((
			relevant_args['SUFFIX'], relevant_args['LANGUAGE']))

	elif '--line-length' in relevant_args:
		try:
			int(relevant_args['INTEGER'])
			database = db.Database()
			database.set_config_item('console_linelength', unicode(relevant_args['INTEGER'].strip(), 'utf-8'))
			print "Setting your console line length to {0} successfull.".format(relevant_args['INTEGER'])
		except ValueError:
			print "Console line length must be an integer."
	
	else:
		determine_proceeding(relevant_args)


def split_arguments(arguments):
	"""Splits the given arguments from the command line in content and flags.

	"""

	request, flags = {}, {}
	for key, item in arguments.iteritems(): 
		if key in ('-e', '-c', '-a', '-d', '-f', '--cut', '--hline', '--suffix'):
			flags[key] = item
		else:
			request[key] = item 

	return (request, flags)


def determine_proceeding(relevant_args):
	""" Checks which operation (add, display, ...)
		needs to be handled. 
	"""

	body, flags = split_arguments(relevant_args)

	if '-f' in flags:
		process_file_adding(body)
	elif '-d' in flags:
		determine_display_operation(body, flags)
	elif '-a' in flags:
		process_add_content(body, flags)
	elif '-c' in flags:
		process_code_adding(body)
	else:
		print "An unexpected error has occured while processing {0} with flags {1}".format(body, flags)


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
	print prewritten_data.splitlines()[0]

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
			choice = raw_input("Output longer than 25 lines - print to console anyway? (y/n) ").strip().split(" ")[0]
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

	with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmpfile:
		if existing_code:
			tmpfile.write(prewritten_data)
			tmpfile.seek(0)
		file_name = tmpfile.name

		if sys.platform == "win32": # windows doing windows things
			try:
	  			subprocess.Popen(editor_list + [tmpfile.name])
	  		except (OSError, IOError) as error:
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

	suffix = check_for_suffix(body['LANGUAGE'], database)
	body['data'] = code_input_from_editor(suffix, database, existing_code)

	try:
		body['data'] = unicode(body['data'], 'utf-8')
	except UnicodeError as error:
		print error

	if body['data'] == existing_code:
		print 'Nothing changed :)'		
	else:
		body['attribute'] = "code"
		database.upsert_code(body) 

	print "Finished - updated your codedict successfully."


###FILE ###

def process_file_adding(body):
	"""Processes adding content to DB from a file.

	"""
	
	try:
		with open(body['PATH-TO-FILE']) as input_file:
			file_text = input_file.read()
			input_file.close()
	except (OSError, IOError) as error:
		print "File Error({0}): {1}".format(error.errno, error.strerror)
		sys.exit(1)

	all_matches = (re.findall(r'%.*?\|(.*?)\|[^\|%]*?\|(.*?)\|[^\|%]*\|(.*?)\|', 
		file_text, re.UNICODE))

	database = db.Database()
 	database.add_content(all_matches, body['LANGUAGE'])
 	print "Finished - updated your codedict successfully."

	
###ADD ###

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

	if body['attribute'] != 'DEL': 
		valid_input = False
		while not valid_input:
			try:
				body['data'] = unicode(raw_input("Change "+body['attribute']+" : ").strip(), 'utf-8')
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

	for index, item in enumerate(('usage: ', 'execution: ', 'comment: ')):
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
 

def determine_display_operation(body, flags):
	"""Processes display actions, checks if a nice form has to be provided or not.

	"""

	
	if '--cut' in flags and 'USAGE' in body:
		cut_usecase = body['USAGE']
	else:
		cut_usecase = False

	if '--hline' in flags:
		hline = True 
	else:
		hline = False

	database = db.Database()

	if '-e' in flags:
		if not 'USAGE' in body:
			body['USAGE'] = ""
		results = database.retrieve_content(body, "full")
		column_list = ["Index", "usage", "execution", "comment", "code added?"]
	
	elif not 'USAGE' in body:
		results = database.retrieve_content(body, "language")
		column_list = ["Index", "usage", "execution", "code added?"]			

	else:
		results = database.retrieve_content(body, "basic")
		column_list = ["Index", "usage", "execution", "code added?"]
	

	if results:
		console_linelength = database.get_config_item('console_linelength')
		if not console_linelength:
			console_linelength = 80
		else:
			console_linelength = int(console_linelength[0])

		updated_results, table = build_table(column_list, results, cut_usecase, hline, console_linelength)
		tmpfile = process_printing(table, database)  # tmpfile gets returned so it can be removed from os.
	
		process_follow_up_operation(body, updated_results, database, tmpfile)

	else:
		print "No results."
		

def build_table(column_list, all_rows, cut_usecase, hline, line_length):
	"""Builds table and prints it to console.

	"""

	#column list length(-1)
	cl_length = len(column_list)-1
	
	result_table = prettytable.PrettyTable(column_list)
	if hline:
		result_table.hrules = prettytable.ALL 

	all_rows_as_list = []

	for row in all_rows:
		single_row = list(row)			# row is a tuple and contains db query results.
		for index in range(1, cl_length): 	# code and index dont need to be filled
			if cut_usecase and index == 1:
				single_row[index] = single_row[index].replace(cut_usecase, "", 1) 
			if not single_row[index]:
				single_row[index] = ""

			dedented_item = textwrap.dedent(single_row[index]).strip()
			single_row[index] = textwrap.fill(dedented_item, width=line_length/(cl_length+1))	

		#if code is present, print "yes", else "no"	
		if single_row[cl_length]:
			single_row[cl_length] = "yes"
		else:
			single_row[cl_length] = "no" 

		#add modified row to table, add original row to return-list
		result_table.add_row(single_row)
		all_rows_as_list.append(list(row))

	return (all_rows_as_list, result_table)


###SECOND ###

def prompt_by_index(results, tmpfile=False):
	"""Prompts the user for further commands after displaying content.
	   Valid input: INDEX [ATTRIBUTE] 
	"""

	valid_input = False 
	while not valid_input:
		user_input = (raw_input(
		"Do you want to do more? Valid input: INDEX [ATTRIBUTE] - Press ENTER to abort: \n")
		.strip().split(None, 1))
		
		if tmpfile:
			try:
				os.remove(tmpfile.name)
				tmpfile = False
			except OSError as error:
				print error 
				print "This error is not crucial for the program itself."


		if not user_input:
			# aborted
			sys.exit(0)
		index = user_input[0]
		try:
			attribute = user_input[1].lower()
		except IndexError:
			attribute = ""

		print attribute

		if len(user_input) <= 2 and index.isdigit() and int(index) >= 1 and int(index) <= len(results):	
			actual_index = int(index)-1
			valid_input = True
			if attribute: 
				if not attribute in ('usage', 'execution', 'comment', 'code', 'del'):
					print "Wrong attribute, Please try again."
					valid_input = False
				else:
					if attribute == 'code':
						attribute = ""
		else:
			print "Wrong index, Please try again."
	return (results[actual_index], attribute) 		


def process_follow_up_operation(original_body, results, database, tmpfile):
	"""Processes the 2nd operation of the user, e.g. code adding.

	"""

	target, attribute = prompt_by_index(results, tmpfile)
	original_body['USAGE'] = target[1]
	
	if attribute:
		original_body['attribute'] = attribute
		return update_content(original_body, database=database)
	else:
		code_of_target = target[len(target)-1]
		if not code_of_target:
			code_of_target = " "
		return process_code_adding(original_body, code_of_target=code_of_target, database=database)

