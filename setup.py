# installation: pip install botoform
from setuptools import (
  setup,
  find_packages,
)

# read requirements.txt for requres, filter comments and newlines.
sanitize = lambda x : not x.startswith('#') and not x.startswith('\n')
with open('requirements.txt', 'r') as f:
    requires = filter(sanitize, f.readlines())

setup( 
    name = 'botoform',
    version = '0.0.1',
    description = 'botoform: Manage AWS Infrastructure with JSON or YAML.',
    keywords = 'botoform manage aws infrastructure json yaml',
    long_description = open('readme.rst').read(),

    author = 'Russell Ballestrini',
    author_email = 'russell@ballestrini.net',
    url = 'https://github.com/russellballestrini/botoform',

    license = 'Apache License 2.0',

    packages = find_packages(),

    install_requires = requires,
    entry_points = {
      'botoform.plugins' : [
        'create = botoform.plugins.create:Create',
        'dump-instances = botoform.plugins.dump:Instances',
        'dump-security-groups = botoform.plugins.dump:SecurityGroups',
        'repl = botoform.plugins.repl:REPL',
      ],
      'console_scripts': [
        'bf = botoform.__main__:main',
      ],
    },
    classifiers=[
        'Intended Audience :: Developers, Operators, System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)

"""
setup()
  keyword args: http://peak.telecommunity.com/DevCenter/setuptools
configure pypi username and password in ~/.pypirc::
 [pypi]
 username:
 password:
build and upload to pypi with this::
 python setup.py sdist bdist_egg register upload
"""
