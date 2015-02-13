"""processes the command line args.

"""

import database 
import ConfigParser
import tempfile
import time
import re
from prettytable import PrettyTable
from subprocess import call 


def start_process(args):
	"""starts processing the command line args.

	"""

	relevant_args = ({key: value for key, value in args.iteritems() if value})
	return check_operation(relevant_args)


def read_config(requested_item, section):
	"""Reads the config file.

	"""


	config = ConfigParser.RawConfigParser()
	path_to_cfg = '../res/codedict_config.cfg'
	print path_to_cfg
	config.read(path_to_cfg)
	try:
		return config.get(section, requested_item)
	except:
		#PROPER exception handling
		print "Exception was raised READ CONFIG"
	return False


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


def display_content_input_form(content, results = False):
	"""Sets up a nice input form (editor) for viewing a large amount of content. -> Read only


	"""

	editor = check_for_editor()

	initial_message = results.get_string()
	print initial_message

	with tempfile.NamedTemporaryFile() as tmpfile:
		tmpfile.write(initial_message)
		tmpfile.flush()
  		call(editor + [tmpfile.name])
  	return True

def check_for_editor():
	"""Checks if the editor is set and if not prompts the user to enter it.

	"""

	if read_config('editor', 'Section1') == False:
		try:
			write_config({'editor' : raw_input("Enter your editor:")}, 'Section1')
		except:
			print "Exception"
	editor = read_config('editor', 'Section1')
	if editor == 'subl' or editor == 'sublime' or editor == 'sublime_text':
		editor = [editor, '-w', '-n']
	else: editor = [editor]
	return editor


def code_input_form(content, existent_code=False):
	"""Sets up a nice input form for code adding and viewing.


	"""

	editor = check_for_editor()

	my_suffix = read_config(content['<language>'], 'Section2')
	if my_suffix == False:
		my_suffix = raw_input("Enter suffix for language '{0}':".format(content['<language>']))
		write_config({content['<language>'] : my_suffix}, 'Section2')

	initial_message = existent_code[0].decode('utf-8')

	with tempfile.NamedTemporaryFile(delete=False, suffix=my_suffix) as tmpfile:
		if existent_code:
			tmpfile.write(initial_message)
		tmpfile.flush()
  		call(editor + [tmpfile.name])
  	with open(tmpfile.name) as my_file:
  		return my_file.read() 
    

def check_operation(relevant_args):
	""" Checks which operation (add, display, ...)
		needs to be handled. 

	"""
	
	content, flags = split_arguments(relevant_args)
	print content
	print flags

	if '-f' in flags:
		del flags['-f']
		return process_file_adding(content)
	if '-d' in flags:
		del flags['-d']
		return process_display_content(content, flags)
	elif '-a' in flags:
		del flags['-a']
		return process_add_content(content, flags)
	elif '-c' in flags:
		del flags['-c']
		return process_code_adding(content)
	else:
		print """An unexpected error has occured 
				while processing {0} with flags {1}
				""".format(content, flags)
		return "error"


def process_code_adding(content):
	"""Processes code adding, provides a nice input form for the user.

	"""


	existent_code = database.retrieve_code(content)
	print "Setting up form"
	content['data'] = code_input_form(content, existent_code)
	if content['data'] == existent_code:
		return 'No DB operation needed, nothing changed'
	content['<attribute>'] = "code"
	print content
	start = time.time()
	database.add_content(content, content['<language>'])
	print "end", time.time()-start 
	return "Finished adding code to DB"


def process_file_adding(content):
	"""Processes adding content from a file.

	"""

	with open(content['<path-to-file>']) as input_file:
	    text = input_file.read()

	items = re.findall(r'%\|(.*?)\|[^\|%]*?\|(.*?)\|[^\|%]*\|(.*?)\|', text)	    
	# for item in items:
	# 	print item
	database.add_content(items, content['<language>'], multiple_insert=True)

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

	print flags
	print location	

	if not "<use_case>" in location:
		print "No flags detected"
		print "Getting all shortcuts for {0} from DB".format(location)
		all_results = database.retrieve_lang_content(location)
		print "Getting data from DB"
		print "Result for lang {0} is {1}".format(location['<language>'], all_results)
		return "Finished displaying all shortcuts for 1 language"  
	
	elif not '-e' in flags:
		print "No nice form needed."
		
		if '-s' in flags:
			print "Short version requested."
			all_results = database.retrieve_extended_content(location)
			print "Getting data from DB"
			return "Finished displaying content with comment."
		else:
			print "Only command requested"
			print "Getting data from DB"
			all_results = database.retrieve_content(location)
			return "Finished displaying command."
	
	else:
		print "Displaying all content requested."
		print "Setting up nice input form." 
		all_results = database.retrieve_all_content(location)
		print "Getting data from DB."
		display_content_input_form(location, all_results)
		print "Printing to nice form."
		return "Finished displaying content in editor."


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
	print "Connecting to DB"
	print content
	start = time.time()
	success = database.update_content(content)
	print "end", time.time()-start
	if success:
		print "success"
	else: print "Failure"
	#TODO -I von -i unterscheiden 
	return "Finished adding content to DB"


def insert_content():
	"""Processes how to insert content.

	"""

	content_to_be_added = {}
	content_to_be_added['language'] = unicode(raw_input("language: ").strip(), 'utf-8')
	content_to_be_added['use_case'] = unicode(raw_input("shortcut: ").strip(), 'utf-8')
	content_to_be_added['command'] = unicode(raw_input("command: ").strip(), 'utf-8')
	content_to_be_added['comment'] = unicode(raw_input("comment: ").strip(), 'utf-8')
	#TODO VALIDATE DATA

	lang = content_to_be_added['language']
	success = True
	print "Lang", read_config(lang, 'Section2')
	
	start = time.time()
	db_status = database.create_table(lang)
	print "Time creating Table:", time.time()-start

	if read_config(lang, 'Section2') == False:
		try:
			my_input = raw_input(("Enter file extension for language {0} : ").format(lang))
			write_config({lang : my_input}, 'Section2')
		except:
			print "Exception"	
	
	if success:	
		start = time.time()
		print "Adding {0} to DB".format(content_to_be_added)
		success = database.add_content(content_to_be_added)
		print "Time adding content to DB", time.time()-start
		return success
	else:
		print "error"
		return False

