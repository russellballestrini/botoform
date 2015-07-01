How to setup Sphinx
#####################

This document explains how to both setup a Sphinx environment as well as
a Sphinx project. If you are cloning this repo, the Sphinx project itself
was already created.

Setup Sphinx Environment
========================

Create a Python virtualenv to install Sphinx related packages.
Check if virtualenv is installed using::

 which virtualenv

If virtualenv is missing, install it with either `pip` or `easy_install`::

 pip install virtualenv

 # or

 easy_install virtualenv

We confirmed virtualenv is installed. Create a virtualenv named env::

 virtualenv env

Activate the new virtualenv::

 source env/bin/activate

Install Sphinx packages::

 pip install -r requirements-docs.txt

If you are cloning this repo you are done.


Create a Sphinx Project
=======================

If you are cloning this repo, stop.
You do not need to perform the steps in this section.

Create a directory to house the Sphinx project::

 mkdir docs
 cd docs

 # generate a new empty Sphinx Project skeleton.
 # accept the default options for a generic project or customize if needed.
 sphinx-quickstart


Sphinx Anatomy
================

source:
 This directory contains ReStructuredText (rst) sourcecode files that may compile or build to different documentation formats.

build:
 Contains the output from building the rst sourcecode into different documentation formats.


Build HTML and setup test webserver
=====================================

Get a list of possible output formats::

 make

Generate HTML from rst source::

 make html

Setup a test webserver::

 # cd build/html/ && python -m SimpleHTTPServer
 make serve

