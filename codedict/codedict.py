""" 
Let's you compile and access your own personal dictionary 
for programming via the command line with ease.

Usage:
  codedict.py -d <language> <use_case> [-e -s --cut --hline]
  codedict.py -d <language> [-e --cut --hline]
  codedict.py -a 
  codedict.py -f <language> <path-to-file>  
  codedict.py -c <language> <use_case>
  codedict.py --editor=<editor>
  codedict.py (-h | --help)
  codedict.py --version  

              -d          Displays content from dictionary.
              -a          Adds content to dictionary.
              -c          Display and add code examples.
              -f          Load content from file into the dictionary.

Options:
  
  -s          Displays comment additionally.
  -e          Displays every value.
  --cut       Cutting search phrase from output.
  --h_line    Choose 'on' if you wish to have a horizontal line in the output. 

  --help      Show this screen.  
  --version   Show version.

"""

#relative import
from docopt import docopt
from processor import start_process

#import from standard library
import time

if __name__ == '__main__':

    COMMAND_LINE_ARGS = docopt(__doc__, version="codedict v 0.4")

    start = time.time()
    try:
        start_process(COMMAND_LINE_ARGS)
    except KeyboardInterrupt:
        print "\nAborted!"
    finally:
        print "Program ran for:", time.time() - start
