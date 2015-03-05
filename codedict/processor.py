"""processes the command line args.

"""

import database 
import ConfigParser
import tempfile
import re
import time
import prettytable
import subprocess
from textwrap import fill


def start_process(cmd_line_args):
	"""starts processing the command line args.

	"""

	relevant_args = ({key: value for key, value in cmd_line_args.iteritems() if value})
	return check_operation(relevant_args)


def read_config(requested_item, section):
	"""Reads the config file.

	"""


	config = ConfigParser.RawConfigParser()
	path_to_cfg = '../res/codedict_config.cfg'
	config.read(path_to_cfg)
	try:
		return config.get(section, requested_item)
	except:
		#PROPER exception handling
		print "Exception was raised READ CONFIG"
		


def write_config(args, section):
	"""Writes to the config file.

	"""

	config = ConfigParser.RawConfigParser()
	if section not in config.sections():
		config.add_section(section)
	for key in args:
		config.set(section, key, args[key])
	
	with open('../res/codedict_config.cfg', 'a') as configfile:
	    config.write(configfile)


def display_content_nice_form(results):
	"""Sets up a nice input form (editor) for viewing a large amount of content. -> Read only


	"""

	editor = check_for_editor()

	initial_message = results.get_string()
	
	with tempfile.NamedTemporaryFile() as tmpfile:
		tmpfile.write(initial_message)
		tmpfile.flush()
  		subprocess.call(editor + [tmpfile.name])
  	return True

def check_for_editor():
	"""Checks if the editor is set and if not prompts the user to enter it.

	"""

	if read_config('editor', 'Editor') == False:
		try:
			editor = raw_input("Enter your editor:")
			write_config({'editor' :  editor}, 'Editor')
		except:
			print "Exception WRITE cfg"
	if editor == 'subl' or editor == 'sublime' or editor == 'sublime_text':
		editor = [editor, '-w', '-n']
	else: editor = [editor]
	return editor


def check_for_suffix(language):
	"""Checks if the cfg has a suffix for the requested lang, if not 
	   it prompts to specify one.

	"""

	my_suffix = read_config(language, 'Suffixes')
	if my_suffix == False:
		my_suffix = raw_input("Enter suffix for language '{0}':".format(language))
		write_config({language : my_suffix}, 'Suffixes')
	return my_suffix


def code_input_form(content, existent_code=False):
	"""Sets up a nice input form for code adding and viewing.


	"""

	editor = check_for_editor()

	language_suffix = check_for_suffix(content['<language>'])

	initial_message = existent_code[0].decode('utf-8')

	with tempfile.NamedTemporaryFile(delete=False, suffix=language_suffix) as tmpfile:
		if existent_code:
			tmpfile.write(initial_message)
		tmpfile.flush()
  		subprocess.call(editor + [tmpfile.name])
  	with open(tmpfile.name) as my_file:
  		return my_file.read() 
    

def check_operation(relevant_args):
	""" Checks which operation (add, display, ...)
		needs to be handled. 

	"""
	
	requested_content, flags = split_arguments(relevant_args)

	if '-f' in flags:
		return process_file_adding(requested_content)
	elif '-d' in flags:
		return process_display_content(requested_content, flags)
	elif '-a' in flags:
		return process_add_content(requested_content, flags)
	elif '-c' in flags:
		return process_code_adding(requested_content)
	else:
		print """An unexpected error has occured 
				while processing {0} with flags {1}
				""".format(requested_content, flags)
		return "error"


def process_code_adding(content):
	"""Processes code adding, provides a nice input form for the user.

	"""

	existent_code = database.retrieve_content(content, "code")
	
	content['data'] = code_input_form(content, existent_code)

	if content['data'] == existent_code:
		return 'No DB operation needed, nothing changed'
	content['<attribute>'] = "code"
	start = time.time()
	database.add_content(content, content['<language>']) 
	print "end", time.time()-start 
	return "Finished adding code to DB"


def process_file_adding(content):
	"""Processes adding content from a file.

	"""
	
	db_status = database.create_table(content['<language>'])
	if not db_status:
		print "Error creating table"
		return False

	with open(content['<path-to-file>']) as input_file:
	    file_text = input_file.read()

	#TODO: catch wrong input file
	all_matches = re.findall(r'%.*?\|(.*?)\|[^\|%]*?\|(.*?)\|[^\|%]*\|(.*?)\|', file_text, re.UNICODE)
	#TODO: necessary?
	for single_match in all_matches:
		print single_match	    
 	database.add_content(all_matches, content['<language>'])
	

def process_add_content(content, flags):
	"""Processes content adding. 

	"""

	if '-I' in flags or '-i' in flags:
		update_content(content)
	else:
		insert_content()


def process_display_content(location, flags):
	"""Processes display actions, checks if a nice form has to be provided or not.

	"""

	if not "<use_case>" in location:
		process_display_language_content(location)
	
	elif not '-e' in flags:
		print "No nice form needed."
		
		if '-s' in flags:
			print "Short version requested."
			process_display_extended_content(location)
		else:
			print "Only command requested"
			process_display_basic_content(location)
			
	else:
		process_display_full_content(location)


def split_arguments(arguments):
	"""Splits the given arguments from the command line in content and flags.

	"""
	content, flags = {}, {}
	for index, item in arguments.iteritems(): 
		if index in ('-s', '-e', '-I', '-i', '-c', '-a', '-d', '-f'):
			flags[index] = item
		else:
			content[index] = item 
	return (content, flags)


def update_content(content):
	"""Processes how to update content.

	"""

	print "Modifying only 1 attribute called {0}".format(content)
	content['data'] = raw_input()
	start = time.time()
	success = database.update_content(content)
	print "end", time.time()-start
	if success:
		print "success"
	else: print "Failure"
	return "Finished adding content to DB"


def insert_content():
	"""Processes how to insert content.

	"""

	content_to_add = {}

	language = unicode(raw_input("language: ").strip(), 'utf-8')
	content_to_add[0] = unicode(raw_input("shortcut: ").strip(), 'utf-8')
	content_to_add[1] = unicode(raw_input("command: ").strip(), 'utf-8')
	content_to_add[2] = unicode(raw_input("comment: ").strip(), 'utf-8')
	#TODO VALIDATE DATA
	print content_to_add
	
	start = time.time()
	db_status = database.create_table(language)
	if not db_status:
		print "Error while setting up table"
		return False

	print "Time creating table:", time.time()-start

	if read_config(language, 'Suffixes') == False:
		try:
			my_input = raw_input(("Enter suffix for language {0} : ").format(language))
			write_config({language : my_input}, 'Suffixes')
		except:
			print "Exception"	

	start = time.time()
	print "Adding {0} to DB".format(content_to_add)
	value_list = [content_to_add]
	success = database.add_content(value_list, language)
	print "Time adding content to DB", time.time()-start
	return success


def process_display_extended_content(location):
	"""Processes displaying extended content, prints to STDOUT.

	"""

	all_results = database.retrieve_content(location, "extended")
	column_list = ["ID", "use_case", "command", "comment", "code added?"]
	
	updated_results = build_table(column_list, all_results)
	if len(all_results) < 10:
		print_to_console(updated_results)
	process_follow_up_lookup(location, updated_results)
	 


def process_follow_up_lookup(original_request, results):
	"""

	"""
	new_target = prompt_by_index(results)
	print new_target
	original_request['<use_case>'] += new_target
	process_code_adding(original_request)



def process_display_language_content(location):
	"""Processes displaying extended content, prints to STDOUT.

	"""

	all_results = database.retrieve_content(location, "extended")

	
	column_list = ["ID", "use_case", "command", "comment", "code added?"]
	updated_results = build_table(column_list, all_results)
	
	if len(all_results) > 10:
		print_to_console(updated_results) 
	else:
			

def print_to_console(table):
	if table:
		print table
	else:
		print "No results"


def process_display_full_content(location):
	"""Processes displaying full content

	"""
	print "Displaying full content requested."
	all_results = database.retrieve_content(location, "full")
	if all_results:
		display_content_nice_form(all_results)
	else:
		print "No results"
	print "Printing to nice form."
	return "Finished displaying content in editor."


def process_display_basic_content(location):
	"""Processes displaying basic content, prints to STDOUT by default.

	"""

	all_results = database.retrieve_content(location, "basic")
	column_list = ["ID", "use_case", "command", "comment", "code added?"]
	
	updated_results = build_table(column_list, all_results)
	if len(all_results) < 10:
		print_to_console(updated_results)
	process_follow_up_lookup(updated_results)


def build_table(column_list, all_rows):
	"""Builds the PrettyTable and prints it to console.

	"""

	#column list length
	cl_length = len(column_list)-1
	
	result_table = prettytable.PrettyTable(column_list)
	result_table.hrules = prettytable.ALL

	for row in all_rows:
		row_as_list = list(row)
		if row_as_list[cl_length]:
			row_as_list[cl_length] = "yes"
		else:
			row_as_list[cl_length] = "no" 
		result_table.add_row(row_as_list)
	return row_as_list


def prompt_by_index(results):
	"""Prompts the user for further commands after displaying content.
	   Valid input: <index> 
	"""

	index_input = (raw_input(
		"Do you want to do further operations on the results? (CTRL-C to abort): ")
		.split(" "))
	if index_input[0].isdigit():
		if len(index_input) < 2:
			return results[int(index_input[0])-1][1]
	else:
		print "Wrong input"
		return False
	




