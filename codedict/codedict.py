""" 
Let's you compile and access your own personal dictionary 
for programming via the command line with ease.

Usage:
  codedict.py -d <language> <use_case> [-s -e]
  codedict.py -d <language>
  codedict.py -a 
  codedict.py -f <language> <path-to-file>  
  codedict.py -c <language> <use_case>
                 
  codedict.py --editor=<editor>
  codedict.py --cut-search=(on|off)
  codedict.py (-h | --help)
  codedict.py --version  

              -d          Displays content from dictionary.
              -a          Adds content to dictionary.
              -c          Display and add code examples.
              -f          Load content from file into the dictionary.

Options:
  
  -s          Displays comment additionally.
  -e          Displays every value.
  -i -I       Modify only 1 value.

  --help      Show this screen.  
  --version   Show version.

"""

#relative import
from docopt import docopt
from processor import start_process

#import from standard library
import time


if __name__ == '__main__':

    COMMAND_LINE_ARGS = docopt(__doc__, version="codedict v 0.1")

    start = time.time()
    try:
        program_status = start_process(COMMAND_LINE_ARGS)
        print program_status
    except KeyboardInterrupt:
        print "\nAborted!"
    finally:
        print "Program ran for:", time.time() - start
