"""command line dictionary. 

Let's you compile and access your own personal dictionary 
for development via the command line with ease.

Usage:
  codedict.py -d <language> <use_case> [-s -e]
  codedict.py -d <language>
  codedict.py -a (-i | -I) <language> <use_case> <attribute>
  codedict.py -a 
  codedict.py -c <language> <use_case>
  codedict.py (-h | --help)
  codedict.py --version

Options:

  -d          Displays dict content.
  -s          Displays comment additionally.
  -e          Displays every value.
  -a          Adds content to the dict.
  -i          Modify only 1 value.
  -I          Same as -i but overrrides the value.
  -c          Add code examples. 

  -h --help   Show this screen.  
  --version   Show version.

"""

from docopt import docopt
from processor import start_process
import time


if __name__ == '__main__':

    COMMAND_LINE_ARGS = docopt(__doc__, version = "codedict v 0.1")
    start = time.time()
    status = start_process(COMMAND_LINE_ARGS)
    print status
    print time.time() - start