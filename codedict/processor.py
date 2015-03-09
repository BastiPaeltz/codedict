"""processes the command line args.

"""

#relative import
import database as db 

#import from standard library
import tempfile
import re
import time
import prettytable
import subprocess
from textwrap import fill


###GENERAL ###



def start_process(cmd_line_args):
	"""Starts processing the command line args. Filters out unrelevant arguments.

	"""
	relevant_args = ({key: value for key, value in cmd_line_args.iteritems() if value})

	if '--editor' in relevant_args:
		database = db.Database()
		database.set_editor(relevant_args['--editor'])		
	else:
		check_operation(relevant_args)


def split_arguments(arguments):
	"""Splits the given arguments from the command line in content and flags.

	"""
	request, flags = {}, {}
	for key, item in arguments.iteritems(): 
		if key in ('-e', '-I', '-i', '-c', '-a', '-d', '-f', '--cut'):
			flags[key] = item
		else:
			request[key] = item 

	return (request, flags)


def check_operation(relevant_args):
	""" Checks which operation (add, display, ...)
		needs to be handled. 

	"""

	
	body, flags = split_arguments(relevant_args)
	database = db.Database("../res/codedict0_6.DB")


	if '-f' in flags:
		process_file_adding(body)
	elif '-d' in flags:
		determine_display_operation(body, flags)
	elif '-a' in flags:
		process_add_content(body, flags)
	elif '-c' in flags:
		process_code_adding(body, database)
	else:
		print """An unexpected error has occured 
				while processing {0} with flags {1}
				""".format(body, flags)


def check_for_suffix(language, database):
	"""Checks if the DB has a suffix for the requested lang, if not 
	   it prompts to specify one.

	"""

	suffix = database.retrieve_suffix(language)

	if suffix:
		print suffix
		return suffix
	else:
		input_suffix = raw_input("Enter suffix for language " +language+" : ").strip()
		database.set_suffix(language, input_suffix)
		return input_suffix


###OUTPUT ###

def print_to_editor(table, database):
	"""Sets up a nice input form (editor) for viewing a large amount of content. -> Read only


	"""

	editor_string = database.get_editor().decode('utf-8')
	if editor_string:
		editor_args = [argument for argument in database.get_editor().decode('utf-8').split(" ")]
	else:
		while True:
			try:
				editor_value = unicode(raw_input("Enter your editor: "), 'utf-8')
				break
			except UnicodeError as error:
				print error

		database.set_editor(editor_value)

	initial_message = table.get_string() #prettytable to string
	print initial_message
	with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
		tmpfile.write(initial_message)
		tmpfile.flush()
  		subprocess.call(editor_args + [tmpfile.name])
  	return True


def process_printing(table, results, database):
	"""Processes all priting to console or editor.

	"""
	decision = decide_where_to_print(results)
	if decision == 'console':
		print table
	else:
		print_to_editor(table, database) 


def decide_where_to_print(all_results):
	"""Decides where to print to.

	"""

	if len(all_results) < 10:
		return 'console'
	else:
		while True:
			choice = raw_input("More than 10 results - print to console anyway? (y/n)").strip().split(" ")[0]
			if choice in ('y', 'yes', 'Yes', 'Y'):
				return "console"
			elif choice in ('n', 'no', 'No', 'N'):
				return "editor"
			else:
				continue


def code_input_from_editor(language, suffix, existent_code=False):
	"""Sets up a nice input form (editor) for code adding and viewing.


	"""

	editor = [argument for argument in check_for_editor().split(" ")]

	initial_message = existent_code.decode('utf-8')


	with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmpfile:
		if existent_code:
			tmpfile.write(initial_message)
		tmpfile.flush()
  		subprocess.call(editor + [tmpfile.name])
  	with open(tmpfile.name) as my_file:
  		return my_file.read() 


###CODE ###


def process_code_adding(body, database=False, target_code=False):
	"""Processes code adding, provides a nice input form for the user.

	"""

	if not database:
		database = db.Database()

	if not target_code:
		existing_code = database.retrieve_content(body, "code")[0]
	else:
		existing_code = target_code

	suffix = check_for_suffix(body['<language>'], database)
	body['data'] = code_input_from_editor(body['<language>'], suffix, existing_code)

	if body['data'] == existing_code or not body['data'].isalnum():
		return 'No DB operation needed, nothing changed'

	#update DB on change
	body['<attribute>'] = "code"
	start = time.time()

	
	database.update_body(body) 
	print "end", time.time()-start 
	return "Finished adding code to DB"


###FILE ###

def process_file_adding(body):
	"""Processes adding content to DB from a file.

	"""
	
	try:
		with open(body['<path-to-file>']) as input_file:
			file_text = input_file.read()
	except (OSError, IOError) as error:
		print "Error({0}): {1}".format(error.errno, error.strerror)
		return False

	all_matches = (re.findall(r'%.*?\|(.*?)\|[^\|%]*?\|(.*?)\|[^\|%]*\|(.*?)\|[^\|%]*\|(.*?)\|', 
		file_text, re.UNICODE))
	
	# for single_match in all_matches:
	# 	print single_match	    
	database = db.Database()
 	database.add_content(all_matches, body['<language>'])
	

###ADD ###

def process_add_content(body, flags):
	"""Processes content adding. 

	"""

	if '-I' in flags or '-i' in flags:
		update_content(body)
	else:
		insert_content()


def update_content(body, database=False):
	"""Processes how to update body.

	"""
	if not database:
		database = db.Database()

	if body['<attribute>'] != 'DEL': 
		while True:
			try:
				body['data'] = unicode(raw_input("Change "+body['<attribute>']+" : ").strip(), 'utf-8')
				break
			except UnicodeError as error:
				print error
		success = database.update_content(body)		
	else:
		success = database.delete_content(body)
	return success


def insert_content():
	"""Processes how to insert content.

	"""

	content_to_add = {}
	while True:
		try:
			language = unicode(raw_input("Enter language: ").strip(), 'utf-8')
			break
		except UnicodeError as error:
			print error

	for index, item in enumerate(('shortcut: ', 'command: ', 'comment: ', 'link: ')):
		while True:
			try: 
				content_to_add[index] = unicode(raw_input("Enter "+ item).strip(), 'utf-8') 
				break
			except UnicodeError as error:
				print error

	database = db.Database()
	start = time.time()
	print "Adding {0} to DB".format(content_to_add)
	success = database.add_content([content_to_add], language) # db function works best with lists
	print "Time adding content to DB", time.time()-start
	return success


### DISPLAYING ###
 

def determine_display_operation(body, flags):
	"""Processes display actions, checks if a nice form has to be provided or not.

	"""

	cut_usecase = False
	if '--cut' in flags:
		cut_usecase = body['<use_case>']
	
	if '--hline' in flags:
		hline = True 
	else:
		hline = False

	database = db.Database()

	if not '<use_case>' in body:
		results = database.retrieve_content(body, "language")
		column_list = ["Index", "use case", "command", "code added?"]
	
	elif not '-e' in flags:

		print "Only command requested"
		results = database.retrieve_content(body, "basic")
		column_list = ["Index", "use case", "command", "code added?"]			
	else:
		results = database.retrieve_content(body, "full")
		column_list = ["Index", "use case", "command", "comment", "code added?"]
	

	if results:
		updated_results, table = build_table(column_list, results, cut_usecase, hline)
		process_printing(table, results, database)
	else:
		print "No results"
		return False
	process_follow_up_lookup(body, updated_results, database)



def build_table(column_list, all_rows, cut_usecase, hline):
	"""Builds the PrettyTable and prints it to console.

	"""

	#column list length
	cl_length = len(column_list)-1
	print cl_length
	
	result_table = prettytable.PrettyTable(column_list)
	if hline:
		result_table.hrules = prettytable.ALL 

	all_rows_as_list = []

	for row in all_rows:
		single_row = list(row)
		print single_row
		
		for index in range(1, cl_length - 1): # code and index dont need to be filled
			if cut_usecase and index == 1:
				single_row[index] = single_row[index].replace(cut_usecase, "", 1) 
			single_row[index] = fill(single_row[index], width=80/(cl_length+1))

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

def prompt_by_index(results):
	"""Prompts the user for further commands after displaying content.
	   Valid input: <index> [attribute] 
	"""

	valid_input = False

	while not valid_input:

		user_input = (raw_input(
		"Do you want to do further operations on the results? (CTRL-C to abort): ")
		.strip().split(" "))
		
		index = user_input[0]
		try:
			attribute = user_input[1]
		except IndexError:
			attribute = ""

		if len(user_input) <= 2 and index.isdigit() and int(index) >= 1 and int(index) <= len(results):	
			actual_index = int(index)-1
			valid_input = True
			if attribute: 
				if not attribute in ('use_case', 'command', 'comment', 'DEL'):
					print "Wrong attribute, Please try again."
					valid_input = False
		else:
			print "Wrong index, Please try again."
	return (results[actual_index], attribute) 		


def process_follow_up_lookup(original_body, results, database):
	"""Processes the 2nd operation of the user, e.g. code adding.

	"""

	target, attribute = prompt_by_index(results)

	if '<use_case>' in original_body:
		original_body['<use_case>'] += target[1]
	else:
		original_body['<use_case>'] = target[1]
	
	if attribute:
		print original_body
		original_body['<attribute>'] = attribute
		return update_content(original_body, database=database)
	else:
		target_code = target[len(target)-1]
		if not target_code:
			target_code = "\n"
		return process_code_adding(original_body, target_code=target_code, database=database)

