"""processes the command line args.

"""

import database
import ConfigParser
import tempfile
from subprocess import call


def start_process(args):
	"""starts processing the command line args

	"""
	relevant_args = ({key: value for key, value in args.iteritems() if value})
	return check_operation(relevant_args)


def read_config(requested_item):
	"""Reads the config file.

	"""

	config = ConfigParser.RawConfigParser()
	config.read('codedict_config.cfg')
	try:
		return config.get('Section1', requested_item)
	except:
		print "Exception was raised"
	return False

def write_config(args):
	"""Writes to the config file.

	"""

	config = ConfigParser.RawConfigParser()
	if 'Section1' not in config.sections():
		config.add_section('Section1')
	for key in args:
		config.set('Section1', key, args[key])
	
	with open('codedict_config.cfg', 'wb') as configfile:
	    config.write(configfile)


def check_operation(relevant_args):
	""" Checks which operation (add, display, ...)
		needs to be handled. 

	"""
	
	content, flags = split_arguments(relevant_args)
	print content
	print flags

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
				while parsing {0} with flags {1}
				""".format(content, flags)
		return "error"

def process_code_adding(content):
	"""Processes code adding, provides a nice input form for the user.

	"""

	print "Setting up form"


	if read_config('editor') == False:
		try:
			write_config({'editor' : raw_input("Enter your editor:")})
		except:
			print "Exception"
	editor = read_config('editor')
	if editor == 'subl' or editor == 'sublime' or editor == 'sublime_text':
		editor = [editor, '-w', '-n']
	code_data = ""
	with tempfile.NamedTemporaryFile(delete = False, suffix="."+content['<language>']) as tmpfile:
  		call(editor + [tmpfile.name])
  		tmpfile.seek(0)
  		print tmpfile.read()
	print code_data
	content['data'] = code_data
	print content['data']
	content['<attribute>'] = "code"
	print content
	database.change_content(content) 
	return "Finished adding code to DB"


def process_add_content(content, flags):
	"""Processes content adding. 

	"""

	if '-I' in flags or '-i' in flags:
		print "Modifying only 1 attribute called {0}".format(content)
		content['data'] = raw_input()
		print "Connecting to DB"
		print content
		success = database.change_content(content)
		if success:
			print "success"
		else: print "Failure"
		#TODO -I von -i unterscheiden 
		return "Finished adding content to DB"
	else:
		content_to_be_added = {}
		content_to_be_added['language'] = raw_input("Language:").strip()
		content_to_be_added['use_case'] = raw_input("Shortcut:").strip()
		content_to_be_added['command'] = raw_input("command:").strip()
		content_to_be_added['comment'] = raw_input("comment:").strip()
		#TODO VALIDATE DATA
		print "Adding {0} to DB".format(content_to_be_added)
		success = database.add_content(content_to_be_added)
		if success:
			print "success"
		else: print "Failure"

def process_display_content(location, flags):
	"""Processes display actions, checks if a nice form has to be provided or not.

	"""

	print flags
	print location	
	if not "<use_case>" in location:
		print "No flags detected"
		print "Getting all shortcuts for {0} from DB".format(location)
		data = database.retrieve_lang_content(location)
		print "Getting data from DB"
		all_results, location = data[0], data[1]
		print "Result for lang {0} is {1}".format(location['<language>'], all_results)
		return "Finished displaying all shortcuts for 1 language"  
	
	elif not '-e' in flags:
		print "No nice form needed."
		
		if '-s' in flags:
			print "Short version requested."
			data = database.retrieve_extended_content(location)
			print "Getting data from DB"
			all_results, location = data[0], data[1]
			print "Result for usecase {0} lang {1} is {2}".format(location['<use_case>'], location['<language>'], all_results)
			return "Finished displaying content with comment."
		else:
			print "Only command requested"
			print "Getting data from DB"
			data = database.retrieve_content(location)
			all_results, location = data[0], data[1]
			print "Result for usecase {0} in lang {1} is {2}".format(location['<use_case>'], location['<language>'], all_results)
			return "Finished displaying command."
	
	else:
		print "Got displaying all content requested."
		print "Setting up nice input form." 
		data = database.retrieve_all_content(location)
		print "Getting data from DB."
		all_results, location = data[0], data[1]
		print "Result for usecase {0} in lang {1} is {2}".format(location['<use_case>'], location['<language>'], all_results)
		print "Printing to nice form."
		return "Finished displaying content in nice form."


def split_arguments(arguments):
	"""Splits the given arguments from the command line in content and flags.

	"""
	content, flags = {}, {}
	for index, item in arguments.iteritems(): 
		if index in ('-s', '-e', '-I', '-i', '-c', '-a', '-d'):
			flags[index] = item
		else:
			content[index] = item 
	return (content, flags)
