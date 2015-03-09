from distutils.core import setup
import sys
import os


DB_NAME = 'codedict_db.DB'

if sys.platform == 'win32':
    data_location = '../data'
    data_files = [(data_location, ['res/'+DB_NAME])]
else:
    data_location = '/usr/share/codedict/'
    if os.path.exists(data_location + DB_NAME):
        data_files = ""
    else:
        data_files = [(data_location, ['res/'+DB_NAME])]  

classifiers=[
       'Development Status :: 4 - Beta',
       'Intended Audience :: Developers',
       'Topic :: Software Development :: Assistance tool',
       'License :: OSI Approved :: MIT License',
       'Programming Language :: Python :: 2.7',
   ],

setup(name='codedict',
      version='0.7',
      description='CLI dictionary for the developer, who likes it organized.',
      author='Sebastian Gabriel Paeltz',
      author_email='bastipaeltz@googlemail.com',
      license='MIT',
      packages=['codedict'],
      data_files=data_files,
      classifiers=classifiers,
      keywords='dictionary documentation cli developer',
      )
