"""
Processes the command line args. --> logic
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
    """
    Starts processing the command line args. Filters out unrelevant arguments.
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
    """
    Sets the wait option to either on or off.
    """

    value = ""
    if 'on' in option:
        value = "on"
        print "Enabling 'wait' option."
    else:
        print "Disabling 'wait' option."

    database = db.Database()
    database.set_config_item('wait', value)
    sys.exit(0)

def set_editor(editor):
    """
    Sets the editor (in the database).
    """

    database = db.Database()
    database.set_config_item('editor', editor.strip())
    print "Setting editor {0} successfull.".format(editor.encode('utf-8'))

def set_suffix(suffix, language):
    """
    Sets the suffix for a specific language (in the database).
    """

    database = db.Database()    
    database.set_suffix(language.strip(), suffix)
    print "Setting suffix {0} for {1} successfull.".format(
        suffix.encode('utf-8'), language.encode('utf-8'))

def set_line_length(length):
    """
    Sets the console's line length.
    """

    try:
        int(length)
        database = db.Database()
        database.set_config_item('linelength', length.encode('utf-8'))
        print "Setting your console line length to {0} successfull.".format(length)
    except ValueError:
        print "Console line length must be an integer."

def split_arguments(arguments):
    """
    Splits the given arguments from the command line in content and flags.
    Returns: Tuple filled with 2 dictionaries.
    """

    request, flags = {}, {}
    for key, item in arguments.iteritems(): 
        if key in ('-c', '-e' '-l', '-a', '-d', '-f', '-t', 
            '--hline', '--suffix', '--open'):
            flags[key] = item
        else:
            request[key.lower()] = item 

    return (request, flags)

def determine_proceeding(body, flags):
    """ 
    Checks which operation (add, display, ...) needs to be handled. 
    """

    if '-f' in flags:
        process_file_adding(body)
    elif '-d' in flags:
        determine_display_operation(body, flags)
    elif '-t' in flags:
        show_tags(body)
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

    if suffix[0]:
        return suffix[0]
    else:
        input_suffix = process_and_validate_input("Enter file suffix for language " +language+" : ")
        database.set_suffix(language, input_suffix)
        return input_suffix

###OUTPUT ###

def check_for_editor(database):
    """
    Checks for editor in the Database. If none is specified, it prompts to enter one.
    """

    editor = database.get_config_item('editor')

    if not editor:
        editor = process_and_validate_input("Enter your editor: ")
        database.set_config_item('editor', editor)
        editor = editor.encode('utf-8')
    else:
        editor = editor[0].encode('utf-8')

    return editor

def editor_to_list(database):
    """
    Gets editor and turns it into list.
    """

    editor_value = check_for_editor(database)
    # subprocess works best with lists instead of strings
    editor_list = [argument for argument in editor_value.split(" ")]
    return editor_list

def print_to_editor(table, database):
    """
    Sets up a nice input form (editor) for viewing a large amount of content. 
    Checks for editor -> Turns result into List -> Writes data (if present) to file ->
    Opens the (temporary) file.
    Returns: tempfile so it can be removed
    """

    editor = editor_to_list(database)

    prewritten_data = table.get_string() # prettytable to string

    with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
        try:
            tmpfile.write(prewritten_data)
            tmpfile.flush()
            try:
                subprocess.Popen(editor + [tmpfile.name])
            except (OSError, IOError) as error:
                print "Error calling your editor - ({0}): {1}".format(error.errno, error.strerror)
                sys.exit(1)

        except (OSError, IOError) as error:
            print error
            sys.exit(1)
    return tmpfile

def process_printing(table, database):
    """
    Processes all priting (to console or editor).
    """

    decision = decide_where_to_print(table)

    if decision == 'console':
        print table
        tmpfile = False
    else:
        tmpfile = print_to_editor(table, database) 
    return tmpfile

def decide_where_to_print(table):    
    """
    Decides where to print to. If output is too long (<25 lines), 
    user gets asked where to print. 
    """

    if len(table.get_string().splitlines()) < 25: # output smaller than 25 lines
        return 'console'
    else:
        decision = ""
        while decision == "":
            choice = process_and_validate_input("Output longer than 25 lines -" 
                "print to console anyway? (y/n)")

            if choice in ('y', 'yes', 'Yes', 'Y'):
                decision = "console"
            elif choice in ('n', 'no', 'No', 'N'):
                decision = "editor"
            else:
                continue
        
        return decision        

def input_from_editor(database, existing_content="", suffix=""):
    """
    Sets up a editor for code (solution) adding and viewing.
    Checks for editor -> Turns into list -> Check if wait is enabled ->
    Opens tempfile ->  When user is done with editing : Returns content of file ->
    Tries to delete file.
    """

    editor = editor_to_list(database)

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
                subprocess.Popen(editor + [tmpfile.name])
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
        else:     # platform != windows
            try:
                subprocess.call(editor + [tmpfile.name])
            except (OSError, IOError) as error:
                print "Error calling your editor - ({0}): {1}".format(error.errno, error.strerror)
                sys.exit(1)

    # no matter what platform from now on
        return read_and_delete_tmpfile(file_name)

###CODE ###

def process_code_adding(body, database=False, code_of_target=False):
    """
    Processes code (solution) adding.
    Gets already present content from database -> Gets language suffix -> 
    Input from editor -> Save content to database.
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

def process_file_adding(body):
    """
    Processes adding content to DB from a file.
    Opens file -> Reads its content -> 
    Either match with regex pattern or simply save in DB. 
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
    if 'problem' in body:
        body['data'] = file_text
        database.upsert_solution(body)    
    else:
        all_matches = (re.findall(r'%[^\|%]*?\|([^\|]*)\|[^\|%]*?\|([^\|]*)\|[^\|%]*\|([^\|]*)\|', 
        file_text, re.UNICODE))
        database.add_content(all_matches, body['language'])
    print "Finished - updated your codedict successfully."

## LINKS

def process_links(body, flags):
    """
    Processes links. Determines proceeding.
    """

    # add links
    if '--open' not in flags: 
        if 'link_name' not in body:

            # set name based on url scheme 
            body['link_name'] = set_link_name(body)

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

def set_link_name(body):
    """
    Sets the link name if not given, based on the url scheme.
    """
    
    entire_url = urlparse.urlsplit(body['url'])
    for url_part in reversed(entire_url):
        if url_part:
            subpart = url_part.split("/")
            link_name = subpart[len(subpart)-1].replace('.html', '')
            break
    if not entire_url.scheme:
        return "http://"+link_name
    else:
        return link_name

def run_webbrowser(url):
    """
    Runs the url in the webbrowser (and surpresses output).
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
    """
    Processes how to update content and saves it to database. (delete or add)
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
    """
    Processes how to insert content.
    Input (and validation) from user for all required fields -> Save to database
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


### DISPLAYING ###

def determine_display_operation(body, flags):
    """
    Processes display actions, checks if a nice form has to be provided or not.
    Get content from database -> get console line length -> build (output) table ->
    Perform follow up operation. 
    """

    args_dict = build_args_dict(body, flags)

    database = db.Database()

    display_type = "display"

    results = []
 
    if '-t' in flags:
        display_type = "tag"
        results, column_list = get_dict_results(database, body, flags)

    elif '-l' in flags:
        display_type = "link"
        results, column_list = get_link_results(database, body)
    
    else:
        results, column_list = get_dict_results(database, body, flags)

    if results:

        console_linelength = get_console_length(database) 

        updated_results, table = build_table(column_list, results, console_linelength, args_dict)
        # tmpfile gets returned so it can be removed from os.
        tmpfile = process_printing(table, database)  
        state = State(database, body, flags, updated_results)
        state.process_follow_up_operation(display_type, tmpfile)
    else:
        print "No results."

def get_link_results(database, body):
    """
    Gets all results for link query from DB and returns the column list additionally.
    """

    if 'searchpattern' not in body:
        body['searchpattern'] = ""  
        results = database.retrieve_links(body, 'display')
        column_list = ["index", "link name", "url", "language"]
    
    else:
        results = database.retrieve_links(body, 'lang-display')            
        column_list = ["index", "link name", "url"]

    return (results, column_list)
        
def get_dict_results(database, body, flags):
    """
    Gets all results for dict query from DB and returns the column list additionally.
    """

    if '-t' in flags:
        if not 'searchpattern' in body:
            body['searchpattern'] = ""
        results = database.retrieve_dict_per_tags(body)            
        column_list = ["index", "problem", "solution"]

    elif 'searchpattern' not in body:
        results = database.retrieve_content(body, "language")
        column_list = ["index", "problem", "solution preview"]
    
    else:
        results = database.retrieve_content(body, "basic")
        column_list = ["index", "language", "problem", "solution preview"]

    return (results, column_list)

def get_console_length(database):
    """
    Gets console length from DB and sets it appropiately. --> convert to int
    """

    console_linelength = database.get_config_item('linelength')
    if not console_linelength:
        console_linelength = 80
    else:
        console_linelength = int(console_linelength[0])
    return console_linelength

def build_table(column_list, all_rows, line_length, args_dict):
    """
    Builds (pretty)table and prints it to console.
    """

    cl_length = len(column_list)-1
    result_table = prettytable.PrettyTable(column_list)

    if 'hline' in args_dict:
        result_table.hrules = prettytable.ALL 

    all_rows_as_list = []

    field_length = line_length/(cl_length)

    for row in all_rows:
        single_row = list(row)            # row is a tuple and contains db query results.
        
        if not 'link' in args_dict:
            if len(single_row[cl_length]) > 50:
                appended_string = "..."
            else:
                appended_string = ""
            single_row[cl_length] = single_row[cl_length][0:50] + appended_string 

        for index in range(1, cl_length+1):     # code and index dont need to be filled
            if not single_row[index]:
                single_row[index] = ""

            dedented_item = textwrap.dedent(single_row[index]).strip()
            single_row[index] = textwrap.fill(dedented_item, width=field_length)    

        #add modified row to table, add original row to return-list
        result_table.add_row(single_row)
        all_rows_as_list.append(list(row))
    return (all_rows_as_list, result_table)
    
###FOLLOW UP ###
    
class State(object):
    """
    State (table, query results, database etc.) after the initial 'query' gets saved.
    Used for 'displaying' operations only.
    """

    def __init__(self, database, body, flags, query_result):
        self._database = database
        self._results = query_result
        self.body_state = body
        self._original_flags = flags

    def _prompt_by_index(self, prompt, default_attribute, permitted_actions, tmpfile=False):
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
                if attribute and attribute in permitted_actions:
                    valid_input = True
                else:
                    print "Wrong attribute, Please try again."
                    valid_input = False
            else:
                print "Wrong index, Please try again."
        return (self._results[actual_index], attribute)         

    def process_follow_up_operation(self, operation_type, tmpfile):
        """
        Processes the 2nd operation of the user, e.g. code adding.
        Differentiates  between link and dict table (and  permitted actions).
        """

        prompt = "Do you want to do more? Valid input: INDEX [ACTION] - Press ENTER to abort: \n"
        
        # link table
        if operation_type == 'link':
            permitted_actions = ('del', 'name', 'link', 'lang')
            target, attribute = self._prompt_by_index(prompt, 'link', permitted_actions, tmpfile)
            self._link_determine_operation(target, attribute)

        # dict table
        else:
            permitted_actions = ('del', 'problem', 'solution', 'tag')
            target, attribute = self._prompt_by_index(prompt, 'code', permitted_actions, tmpfile)
        
            self.body_state['problem'] = target[1]

            if attribute == 'tag':
                self.update_tag_for_dict()
            elif attribute != 'code':
                self.body_state['attribute'] = attribute
                return update_content(self.body_state, database=self._database) 
            else:
                code_of_target = target[len(target)-1]
                if not code_of_target:
                    code_of_target = " "
                return process_code_adding(self.body_state, 
                code_of_target=code_of_target, database=self._database)

    def update_tag_for_dict(self):
        """
        Retrieves set tags for a certain dict value first, displays them
        and processes input (add or delete tags).
        """

        all_tags = self._database.get_tags(self.body_state)    

        if all_tags:

            print "\nFollowing tags are set for problem '{0}' :".format(self.body_state['problem'])

            for tag in all_tags:
                print "'" + tag[0]+"' ",
            print ""
        else:
            print "\nNo tags set."

        tag_input = ""
        while not (tag_input.startswith('+') or tag_input.startswith('-')):  
            tag_input = process_and_validate_input(
                "Add or remove a tag with '+'TAGNAME or '-'TAGNAME : ")

        self.body_state['tag_name'] = tag_input[1:]
        if tag_input[0] == '+':
            self._database.update_tags(self.body_state, 'add')
            print "Adding tag {0} successful.".format(self.body_state['tag_name'])    
        else:
            self._database.update_tags(self.body_state, 'del')
            print "Deleting tag {0} successful.".format(self.body_state['tag_name'])    
        sys.exit(0)

    def _link_determine_operation(self, target, attribute):
        """
        Determines what operation to do on link table.
        """

        # default - run link in webbrowser
        if attribute == 'link':
            self.body_state['link_name'] = target[1]
            link_url = self._database.retrieve_links(self.body_state, 'open')
            if link_url:
                requested_url = link_url[0]
                if not requested_url.startswith('http'):
                    requested_url = "http://"+requested_url

                run_webbrowser(requested_url)
            else:
                print "No links."
                sys.exit(0)

        elif attribute == 'del':
            self.body_state['url'] = target[2] 
            self._database.delete_links(self.body_state)
            print "Deleting link {0} successfully.".format(target[1].encode('utf-8'))
            sys.exit(0)

        # language to link
        elif attribute == 'lang':
            self.body_state['attribute'] = "language"
            self.body_state['data'] = process_and_validate_input("Change " 
                + self.body_state['attribute']+ "to : ")
            self.body_state['link_name'] = target[1]
        else:
            # attribute = name
            self.body_state['attribute'] = "name"
            self.body_state['data'] = process_and_validate_input("Change " 
                + self.body_state['attribute']+ "to : ")
        
        self.body_state['url'] = target[2]
        self.body_state['original-lang'] = target[-1]
        self._database.upsert_links(self.body_state, operation_type='upsert')
        print "Changing link attribute {0} successfull.".format(
            self.body_state['attribute'].encode('utf-8'))
        sys.exit(0)
    
## HELPER

def process_and_validate_input(prompt):
    """ 
    Processes trivial input and validates it. Returns the user's input.
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
    """
    Determines and sets hline and cutsearch as well as links based 
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
    """
    Converts every value of the input_dict dict which contains strings into unicode.
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
    """
    Reads from tmpfile and tries to delete it afterwards.
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

def show_tags(body):
    """
    Prints all tags, which are set for a certain language to console.
    (Gives option to remove some of them entirely)
    """

    database = db.Database()
    all_tags = database.get_tags(body)

    if not all_tags:
        print "No tags set for language {0}.".format(body['language'])
    else:
        print "\nFollowing tags are set for language '{0}' :".format(body['language'])

        for tag in all_tags:
            print "'" + tag[0]+"' ",

        print ""
        tag_input = ""
        while not tag_input.startswith('-'):  
            tag_input = process_and_validate_input(
                "Remove a tag entirely with '-'TAGNAME : ")

        body['tag_name'] = tag_input[1:]
        database.delete_tag(body)
        print "Deleting tag '{0}'' entirely successful.".format(body['tag_name'])    
        sys.exit(0)
