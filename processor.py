"""processes the command line args.

"""
import database


def start_process(args):
	"""starts processing the command line args

	"""

	relevant_args = ({key: value for key,value in args.iteritems() 
	if value})
	return check_operation(relevant_args)



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

def process_code_adding(location):
	"""Processes code adding, provides a nice input form for the user.

	"""

	print "Setting up form"
	#TODO providing nice form and reading out content 
	code = raw_input().strip()
	print "Got {0} code to process for item {1}".format(code, location)
	# TODO send content to DB like database.add_content(code, location) 
	return "Finished adding code to DB"


def process_add_content(content, flags):
	"""Processes content adding. 

	"""

	if '-I' in flags or '-i' in flags:
		print "Modifying only 1 attribute called {0}".format(content)
		print "Connecting to DB"
		#
		return "Finished adding content to DB"
	else:
		content_to_be_added = {}
		content_to_be_added['language'] = raw_input("Language:")
		content_to_be_added['use_case'] = raw_input("Shortcut:")
		content_to_be_added['command'] = raw_input("command:")
		content_to_be_added['comment'] = raw_input("comment:")
		content_to_be_added['alternatives'] = raw_input("alternatives:")
		print "Adding {0} to DB".format(content_to_be_added)
		print "Connecting to DB"
		return "Finished adding content to DB"

def process_display_content(location, flags):
	"""Processes display actions, checks if a nice form has to be provided or not.

	"""

	print flags
	if not flags:
		print "No flags detected"
		print "Getting all shortcuts for {0} from DB".format(location)
		return "Finished displaying all shortcuts for 1 language"  
	elif not '-e' in flags:
		print "No nice form needed."
		if '-s' in flags:
			print "Short version requested."
			requested_content = 'Short version'
			#return database.display_content(location, requested_content)
			print "Getting data from DB"
			return "Finished displaying content with comment."
		else:
			print "Only command requested"
			print "Getting data from DB"
			return "Finished displaying command."
	else:
		requested_content = 'All'
		print "Got displaying all content requested."
		print "Setting up nice input form." 
		#content = return database.display_content(location, requested_content)
		print "Getting data from DB."
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
	tuple = (content, flags)
	return tuple