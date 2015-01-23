"""processes the command line args.

"""

import database
import ConfigParser
import tempfile
import time
from subprocess import call


def start_process(args):
	"""starts processing the command line args

	"""

	relevant_args = ({key: value for key, value in args.iteritems() if value})
	return check_operation(relevant_args)


def read_config(requested_item, section):
	"""Reads the config file.

	"""

	config = ConfigParser.RawConfigParser()
	config.read('codedict_config.cfg')
	try:
		return config.get(section, requested_item)
	except:
		print "Exception was raised"
	return False


def write_config(args, section):
	"""Writes to the config file.

	"""

	config = ConfigParser.RawConfigParser()
	if section not in config.sections():
		config.add_section(section)
	for key in args:
		config.set(section, key, args[key])
	
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


	if read_config('editor', 'Section1') == False:
		try:
			write_config({'editor' : raw_input("Enter your editor:")}, Section1)
		except:
			print "Exception"
	editor = read_config('editor')
	if editor == 'subl' or editor == 'sublime' or editor == 'sublime_text':
		editor = [editor, '-w', '-n']
	else: editor = [editor]

	my_suffix = read_config('editor', 'Section1')
	if my_suffix == False:
		print "Suffix error"
		my_suffix = ""


	with tempfile.NamedTemporaryFile(delete=False, suffix=my_suffix) as tmpfile:
  		call(editor + [tmpfile.name])
  		tmpfile.file.close()
    	tmpfile = file(tmpfile.name)
    	content['data'] = tmpfile.read()

	print content['data']
	content['<attribute>'] = "code"
	print content
	start = time.time()
	database.update_content(content)
	print "end", time.time()-start 
	return "Finished adding code to DB"


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
	"""Processes how to insert content

	"""

	content_to_be_added = {}
	content_to_be_added['language'] = raw_input("Language: ").strip()
	content_to_be_added['use_case'] = raw_input("Shortcut: ").strip()
	content_to_be_added['command'] = raw_input("command: ").strip()
	content_to_be_added['comment'] = raw_input("comment: ").strip()
	#TODO VALIDATE DATA

	lang = content_to_be_added['language']
	success = True
	print lang
	if read_config(lang, 'Section2') == False:
		try:
			my_input = raw_input(("Enter file extension for language {0}").format(lang))
			write_config({lang : my_input}, 'Section2')
		except:
			print "Exception"

		success = database.create_table(lang)	
	if success:	
		start = time.time()
		print "Adding {0} to DB".format(content_to_be_added)
		success = database.add_content(content_to_be_added)
		print "end", time.time()-start
		return success
	else:
		print "error"
		return False

