"""
Defines the data processing / handling using local sqlite3 database.
"""

# import from standard library
from collections import namedtuple
import sqlite3
import sys
import os
import shutil

# This structures return values form 'Database.get_full_dump'
DumpEntry = namedtuple('DumpEntry', ['language', 'tags', 'problem', 'solution'])

class Database(object):
    """
    DB class, handles all connections with the database.
    """

    def __init__(self):
        self.db_path = determine_db_path()
        if not os.path.isdir(self.db_path):
            print "Building database."
            os.makedirs(self.db_path)
        self._db_instance = establish_db_connection(self.db_path + '/codedict_db.DB')
        self._setup_database()

    def _setup_database(self):
        """
        Sets up the database for usage. Exits if connecting to DB or setting up
        tables fails.
        """

        if not self._db_instance:
            print "Error while reaching DB."
            sys.exit(1)

        if not self._create_tables():
            print "Error while creating DB tables."
            sys.exit(1)

    def _create_tables(self):
        """
        Creates tables 'dictionary', 'languages', 'links' and 'config' if they not exist.
        """

        try:
            with self._db_instance:
                # create tables
                self._db_instance.execute('''
                    CREATE table IF NOT EXISTS Languages (id INTEGER PRIMARY KEY, 
                        language TEXT UNIQUE, suffix TEXT)
                ''')

                self._db_instance.execute('''
                    CREATE table IF NOT EXISTS Tags (id INTEGER PRIMARY KEY, 
                        name TEXT, language TEXT)
                ''')

                self._db_instance.execute('''
                    CREATE table IF NOT EXISTS ItemsToTags (id INTEGER PRIMARY KEY, 
                        tagID INTEGER, dictID INTEGER)
                ''')

                self._db_instance.execute('''
                    CREATE table IF NOT EXISTS Dictionary 
                    (id INTEGER PRIMARY KEY, language TEXT, 
                        problem TEXT, solution TEXT) 
                ''')

                self._db_instance.execute('''
                    CREATE table IF NOT EXISTS Config (configItem TEXT PRIMARY KEY, value TEXT)
                ''')

                self._db_instance.execute('''
                    CREATE table IF NOT EXISTS Links (id INTEGER PRIMARY KEY, name TEXT, 
                    URL text, language TEXT)
                ''')

                return True

        except sqlite3.Error as error:
            print "A database error has ocurred: ", error
            return False

    def rollback(self):
        """
        Rolls back the database to last
        """

        try:
            shutil.copy2(self.db_path + "/BACKUP_codedict_db.DB", self.db_path + "/codedict_db.DB")
        except (shutil.Error, IOError, OSError) as error:
            print "Error while rolling back database.\n", error
            sys.exit(1)

    def get_config_item(self, config_item):
        """
        Gets a config item (editor or line-length) from the Config table.
        """

        try:
            with self._db_instance:
                value = self._db_instance.execute('''
                    SELECT value from Config where configItem = ?
                ''', (config_item, ))

            return value.fetchone()
        except sqlite3.Error as error:
            print "A database error has ocurred: ", error
            sys.exit(1)

    def set_config_item(self, config_item, value):
        """
        Sets the editor row in the Config table of the DB.
        """

        try:
            with self._db_instance:

                self._db_instance.execute('''
                    INSERT or IGNORE INTO Config (configItem, value) VALUES (?, ?)
                ''', (config_item, value, ))

                self._db_instance.execute('''
                    UPDATE Config SET value = ? WHERE configItem = ?
                ''', (value, config_item, ))

        except sqlite3.Error as error:
            print "A database error has ocurred: ", error
            sys.exit(1)

    def retrieve_suffix(self, lang_name):
        """
        Retrieves suffix for 1 language from Language table of the DB. 
        """

        try:
            with self._db_instance:

                suffix = self._db_instance.execute('''
                    SELECT suffix from Languages where language = ?
                ''', (lang_name, ))

            return suffix.fetchone()
        except sqlite3.Error as error:
            print "A database error has ocurred: ", error
            sys.exit(1)

    def set_suffix(self, lang_name, suffix):
        """
        Inserts suffix for 1 language into the DB.
        """

        try:
            with self._db_instance:

                self._db_instance.execute('''
                    INSERT or IGNORE into Languages (language, suffix) VALUES(?,?)
                ''', (lang_name, suffix))

                self._db_instance.execute('''
                    UPDATE Languages SET suffix = ? WHERE language = ?
                ''', (suffix, lang_name, ))

        except sqlite3.Error as error:
            print "A database error has ocurred: ", error
            sys.exit(1)

    def delete_content(self, values):
        """
        Deletes content from the Dictionary table, language and problem field 
        have to match the rows values.
        """

        try:
            with self._db_instance:

                self._db_instance.execute('''
                    DELETE from Dictionary WHERE problem = ? AND language = 
                    (SELECT language from Languages where language = ?)
                ''', (values['problem'], values['language']))

        except sqlite3.Error as error:
            print "A database error has ocurred: ", error
            sys.exit(1)

    def update_content(self, values):
        """
        Updates content of the DB, not insert! Only for values whcih already exist.
        """

        try:
            with self._db_instance:
                # update database

                if values['attribute'] != 'link':
                    self._db_instance.execute('''
                        UPDATE Dictionary SET {0} = ? WHERE problem = ? AND language = 
                        (SELECT language from Languages where language = ?)
                    '''.format(values['attribute']),
                        (values['data'],
                         values['problem'],
                         values['language']))
                else:
                    self._db_instance.execute('''
                        UPDATE Links SET {0} = ? WHERE problem = ? AND language = 
                        (SELECT id from Languages where language = ?)
                    '''.format(values['attribute']),
                        (values['data'],
                         values['problem'],
                         values['language']))

        except sqlite3.Error as error:
            print "A database error has ocurred: ", error
            sys.exit(1)

    def get_full_dump(self, language, required_tags):
        """
        Gets a full dump of all entries which have the given language, and
        all of the given tags. The return value is a list of DumpEntry
        objects.
        """
        required_tags = set(required_tags)
        try:
            with self._db_instance:
                # FIXME: This can probably be done better in pure-SQL, but 30 
                # minutes of web searching hasn't revealed how
                all_problems = self._db_instance.execute(
                    '''
                    SELECT id, language, problem, solution
                    FROM Dictionary
                    ''')

                results = []
                for dict_id, language, problem, solution in all_problems.fetchall():
                    tag_results = self._db_instance.execute(
                        '''
                        SELECT name FROM Tags
                        INNER JOIN ItemsToTags
                        ON ItemsToTags.tagID = Tags.id
                        WHERE ItemsToTags.dictID = ?
                        ''', (dict_id,))
                    tags = set(tag for (tag,) in tag_results)

                    # This is the part of the query difficult to recreate in
                    # SQL - ensuring that the tags on the entry are a superset
                    # of the tags given by the user
                    if required_tags <= tags:
                        results.append(DumpEntry(language, tags, problem, solution))

                return results
        except sqlite3.Error as error:
            print "A database error has ocurred: ", error
            sys.exit(1)

        ### Tags

    def get_tags(self, values):
        """
        Retrieves / gets tags from DB.
        """

        try:
            with self._db_instance:

                if 'problem' in values:
                    results = self._db_instance.execute(
                        '''
                        SELECT name FROM Tags 
                        INNER JOIN ItemsToTags ON Tags.id = ItemsToTags.tagID 
                        WHERE dictID = (SELECT id from Dictionary where language = ? 
                            and problem = ?) 
                        and language = ? 
                        ''', (values['language'], values['problem'], values['language']))

                else:
                    results = self._db_instance.execute(
                        '''
                        SELECT name FROM Tags where language = ?  
                        ''', (values['language'], ))

                return results.fetchall()

        except sqlite3.Error as error:
            print " A database error has ocurred.", error
            sys.exit(1)

    def update_tags(self, values, update_type='add'):
        """
        Updates the tag field of item (link or dict)
        """

        try:
            with self._db_instance:
                if update_type == 'add':
                    self._db_instance.execute('''
                        INSERT or IGNORE into Tags (name, language)
                        VALUES (?, ?)
                    ''', (values['tag_name'], values['language']))

                    self._db_instance.execute('''
                        INSERT or REPLACE into ItemsToTags (tagID, dictID)
                        VALUES (
                        (SELECT id from Tags WHERE name = ? AND language = ?),
                        (SELECT id from Dictionary WHERE problem = ? and language = ?)
                        )''', (values['tag_name'], values['language'], 
                        values['problem'], values['language']))

                #update_type = delete 
                else:
                    self._db_instance.execute('''
                        DELETE from ItemsToTags WHERE dictID = 
                        (SELECT id from Dictionary WHERE problem = ? and language = ?) 
                        AND tagID = (SELECT id from Tags WHERE name = ? AND language = ?)    
                    ''', (values['problem'], values['language'], 
                        values['tag_name'], values['language']))

        except sqlite3.Error as error:
            print "A database error has ocurred: ", error
            sys.exit(1)

    def delete_tag(self, values):
        """
        Deletes the tag and all associated items (link or dict).
        """

        try:
            with self._db_instance:
                self._db_instance.execute(
                    '''
                        DELETE from Tags WHERE name = ? AND language = 
                        (SELECT language from Languages where language = ?)
                    ''', (values['tag_name'], values['language']))

        except sqlite3.Error as error:
            print "A database error has ocurred ", error
            sys.exit(1)

    def retrieve_dict_per_tags(self, values):
        """
        Retrieves dict content based on tags.
        """

        try:
            with self._db_instance:

                results = self._db_instance.execute(
                    '''
                    SELECT DISTINCT problem, solution FROM Dictionary 
                    INNER JOIN ItemsToTags On Dictionary.id = ItemsToTags.dictID
                    INNER JOIN Tags On ItemsToTags.tagID = Tags.id
                    WHERE Tags.language = ? and Tags.name LIKE ?      
                    ''', (values['language'], values['searchpattern'] + '%'))

                return selected_rows_to_list(results)

        except sqlite3.Error as error:
            print "A database error has ocurred ", error
            sys.exit(1)

        ### LINKS

    def upsert_links(self, values, operation_type='add'):
        """
        Upserts (insert or update if exists) links into Link table.
        """

        try:
            with self._db_instance:

                # add link to Links db if not exists
                self._db_instance.execute('''
                    INSERT OR IGNORE INTO Links (id, name, url, language) VALUES 
                    ((SELECT id from Links WHERE name = ? AND language = ?), ?, ?, ?)
                ''', (values['link_name'], values['original-lang'], values['link_name'],
                      values['url'], values['language']))

                if operation_type == 'upsert':
                    self._db_instance.execute('''
                        UPDATE Links SET {0} = ? WHERE name = ? AND url = ? AND language = ?
                    '''.format(values['attribute']), (values['data'], values['link_name'],
                                                      values['url'], values['original-lang']))

        except sqlite3.Error as error:
            print "A database error has ocurred: ", error
            sys.exit(1)

    def delete_links(self, values):
        """
        Deletes links from Link table.
        """

        try:
            with self._db_instance:
                self._db_instance.execute('''
                    DELETE from Links WHERE url = ? 
                ''', (values['url'], ))

        except sqlite3.Error as error:
            print "A database error has ocurred: ", error
            sys.exit(1)

    def retrieve_links(self, values, selection_type):
        """
        Retrieves links into Link table.
        """
        try:
            with self._db_instance:
                if selection_type == 'open':

                    selection = self._db_instance.execute('''
                        SELECT url from Links WHERE name = ? AND language = ? 
                    ''', (values['searchpattern'], values['language']))
                    return selection.fetchone()

                else:  # display

                    if selection_type == 'display':
                        selection = self._db_instance.execute('''
                            SELECT name, url, language from Links WHERE name LIKE ?
                        ''', (values['searchpattern'] + '%', ))

                    elif selection_type == 'lang-display':  # lang display
                        selection = self._db_instance.execute('''
                            SELECT name, url from Links WHERE name LIKE ?
                            AND language = ? 
                        ''', (values['searchpattern'] + '%', values['language']))

                    selection_list = selected_rows_to_list(selection)
                    return selection_list

        except sqlite3.Error as error:
            print "A database error has ocurred: ", error
            sys.exit(1)

    def upsert_solution(self, values):
        """
        Upserts (insert or update if exists) code into the DB. 
        """

        try:
            with self._db_instance:

                #add language to lang db if not exists
                self._db_instance.execute('''
                    INSERT OR IGNORE INTO Languages (language, suffix) VALUES (?, "")
                ''', (values['language'], ))

                self._db_instance.execute('''
                    UPDATE Dictionary SET solution = ? WHERE problem = ? AND language = 
                    (SELECT language from Languages where language = ?)
                    ''', (values['data'],
                          values['problem'],
                          values['language']))

                self._db_instance.execute('''
                    INSERT or IGNORE into Dictionary (id, language, problem, solution)
                    VALUES((SELECT id from Dictionary where problem = ? AND language = 
                    (SELECT language from Languages where language = ?)) 
                    ,(SELECT language from Languages where language = ?), ?, ?)
                ''', (values['problem'],
                      values['language'],
                      values['language'],
                      values['problem'],
                      values['data']))

        except sqlite3.Error as error:
            print "A database error has ocurred: ", error
            sys.exit(1)

    def add_content(self, values, lang_name, insert_type="normal"):
        """
        Adds content to the database. Tries to insert and updates if 
        row already exists.
        """

        # backup database file 
        if insert_type == "from_file":
            try:
                shutil.copy2(self.db_path + "/codedict_db.DB", 
                    self.db_path + "/BACKUP_codedict_db.DB")
            except (shutil.Error, IOError, OSError) as error:
                print "Error while backing up database.", error
                print "Continuing ..."

        try:
            with self._db_instance:
                dict_cursor = self._db_instance.cursor()
                tags_cursor = self._db_instance.cursor()
                #add language to lang db if not exists
                self._db_instance.execute('''
                    INSERT OR IGNORE INTO Languages (language, suffix) VALUES (?, "")
                ''', (lang_name, ))

                for new_row in values:

                    dict_cursor.execute('''
                        INSERT or REPLACE into Dictionary 
                        (id, language, problem, solution)
                        VALUES((SELECT id from Dictionary where problem = ? AND language = 
                        (SELECT language from Languages where language = ?)), 
                        (SELECT language from Languages where language = ?), ?, ?)
                    ''', (new_row[1], lang_name, lang_name, new_row[1], new_row[2]))

                    tags_list = process_input_tags(new_row[0])
                    dict_id = dict_cursor.lastrowid

                    self._db_instance.execute('''
                            DELETE from ItemsToTags where dictID = ? 
                        ''', (dict_id,))

                    for tag in tags_list:
                        tags_cursor.execute('''
                        INSERT OR REPLACE INTO Tags (id, name, language) VALUES (
                            (SELECT id from Tags WHERE name = ? and language = ?), 
                            ?, (SELECT language from Languages where language = ?))
                        ''', (tag.strip(), lang_name, tag.strip(), lang_name))

                        tag_id = tags_cursor.lastrowid
                        
                        self._db_instance.execute('''
                            INSERT OR IGNORE into ItemsToTags (tagID, dictID) VALUES (?, ?)
                        ''', (tag_id, dict_id))

        except sqlite3.Error as error:
            print "A database error has ocurred: ", error
            sys.exit(1)

    def retrieve_content(self, location, selection_type):
        """
        Retrieves content, packs them in indexed tuples if needed
        and sends results back to calling function.
        """

        db_selection = self._select_from_db(location, selection_type)
        if not selection_type == "code":
            selection_result = selected_rows_to_list(db_selection)
        else:
            selection_result = db_selection.fetchone()
        return selection_result  # returns False if no rows were selected

    def _select_from_db(self, location, selection_type):
        """
        Selects from DB. Runs correct query.
        """

        if selection_type not in ('language', 'basic', 'code'):
            print "DB received no valid selection type."
            sys.exit(1)

        try:
            with self._db_instance:

                if selection_type == "basic":

                    selection = self._db_instance.execute('''
                        SELECT language, problem, solution FROM Dictionary WHERE problem LIKE ?
                    ''', (location['searchpattern'] + '%', ))

                elif selection_type == "language":

                    selection = self._db_instance.execute('''
                        SELECT problem, solution FROM Dictionary WHERE language = 
                        (SELECT language from Languages where language = ?) 
                    ''', (location['language'], ))

                elif selection_type == "code":

                    selection = self._db_instance.execute('''
                        SELECT solution FROM Dictionary WHERE problem = ? and language = 
                        (SELECT language from Languages where language = ?)
                        ''', (location['searchpattern'], location['language']))

                return selection

        except sqlite3.Error as error:
            print "A database error has ocurred: ", error
            sys.exit(1)


def selected_rows_to_list(all_rows):
    """
    Packs all results from a SELECT statement into a list of tuples 
    with index attached (at first position).    
    """

    result_list = []
    for count, row in enumerate(all_rows):
        result_list.append((count + 1, ) + row)
    if result_list:
        return result_list
    else:
        return False


def determine_db_path():
    """
    Determines where the DB file is located. If executable is frozen the location 
    differentiates.
    """

    if getattr(sys, 'frozen', False):
        # The application is frozen
        datadir = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        datadir = os.path.dirname(__file__)

    return datadir + '/res'


def establish_db_connection(db_path):
    """
    Establishes the connection to the DB.
    """

    try:
        return sqlite3.connect(db_path)

    except sqlite3.Error as error:
        print "A database error has ocurred: ", error
        return False


def process_input_tags(all_tags):
    """
    Gets input for the tags field, validates them and returns all.
    """

    if ";" in all_tags:
        tag_list = all_tags.split(";")
    else:
        tag_list = [all_tags]
    return tag_list

