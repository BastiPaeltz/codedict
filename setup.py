import sys
from cx_Freeze import setup, Executable

options = {
    'build_exe': {
        'packages': 'codedict',
    }
}

executables = [
    Executable('codedict.py')
]

classifiers=[
       'Development Status :: 4 - Beta',
       'Intended Audience :: Developers',
       'Topic :: Software Development :: Assistance tool',
       'License :: OSI Approved :: MIT License',
       'Programming Language :: Python :: 2.7',
   ],

setup(name='codedict v0.7',
      version='0.7',
      description='CLI dictionary for the developer, who likes it organized.',
      author='Sebastian Gabriel Paeltz',
      author_email='bastipaeltz@googlemail.com',
      license='MIT',
      packages=['codedict'],
      data_files=[('res', ['res/codedict_v071.DB'])],
      options=options,
      classifiers=classifiers,
      keywords='dictionary documentation cli developer',
      executables=executables

      )
