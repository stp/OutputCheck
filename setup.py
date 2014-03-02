#!/usr/bin/env python

from distutils.core import setup
import version

long_description="""
*OutputCheck*
+++++++++++++

About
=====

``OutputCheck`` is a tool for checking the output of console programs
that is inspired by the FileCheck tool used by LLVM. It has its own
small language for describing the expected output of a tool that
is considerably more convenient and more powerful than GNU ``grep``.


Documentation and Source
========================

Documentation and source code can be found at http://github.com/delcypher/OutputCheck
"""

setup(name='OutputCheck',
      version=version.get_git_version(),
      description="A tool for checking the output of console programs inspired by LLVM's FileCheck",
      author='Daniel Liew',
      author_email='delcypher@gmail.com',
      url='http://github.com/delcypher/OutputCheck',
      packages=['OutputCheck'],
      scripts=['bin/OutputCheck'],
      classifiers=[ 'Environment :: Console',
                    'Development Status :: 3 - Alpha',
                    'Intended Audience :: Developers',
                    'License :: OSI Approved :: BSD License',
                    'Natural Language :: English',
                    'Operating System :: OS Independent', # Not tested
                    'Programming Language :: Python :: 2.7',
                    'Programming Language :: Python :: 3',
                    'Topic :: Software Development :: Testing',
                    'Topic :: Text Processing',
                    'Topic :: Utilities'
                  ],
      long_description=open('pypi_description.rst','r').read()
     )
