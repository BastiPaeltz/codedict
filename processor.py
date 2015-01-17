"""processes the command line args.

"""

import database


def start_process(args):
	"""starts processing the command line args

	"""

	relevant_args = ({key: value for key, value in args.iteritems() 
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

def process_code_adding(content):
	"""Processes code adding, provides a nice input form for the user.

	"""

	print "Setting up form"
	#TODO providing nice form and reading out content 
	content['data'] = raw_input().strip()
	content['attribute'] = "code"
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
		content_to_be_added['language'] = raw_input("Language:")
		content_to_be_added['use_case'] = raw_input("Shortcut:")
		content_to_be_added['command'] = raw_input("command:")
		content_to_be_added['comment'] = raw_input("comment:")
		print "Adding {0} to DB".format(content_to_be_added)
		success = database.add_content(content_to_be_added)
		if success:
			print "success"
		else: print "Failure"

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
			requested_content = 'comment'
			data = database.display_content(location, requested_content)
			print "Getting data from DB"
			all_results, location = (*data)
			print "Result for lang {1} is {2}"
					.format(location['language'], all_results)
			return "Finished displaying content with comment."
		else:
			print "Only command requested"
			print "Getting data from DB"
			data = database.display_content(location)
			all_results, location = (*data)
			print "Result for usecase {0} in lang {1} is {2}"
					.format(location['use_case'], location['language'], all_results)
			return "Finished displaying command."
	else:
		location['use_case'] = '*'
		print "Got displaying all content requested."
		print "Setting up nice input form." 
		data = database.display_content(location)
		print "Getting data from DB."
		all_results, location = (*data)
		print "Result for usecase {0} in lang {1} is {2}"
				.format(location['use_case'], location['language'], all_results)
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
