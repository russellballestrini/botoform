bf plugins
###########

.. note:: For working examples see the `plugins <https://github.com/russellballestrini/botoform/tree/master/botoform/plugins>`_ directory.

You may extend the ``bf`` tool by writing a plugin.

A ``bf`` plugin must take one of two forms:

#. `function plugin`_
#. `class plugin`_

All ``bf`` subcommands have been implemented in this way.

In your plugin project's *setup.py* create an `entry point`_ in the
``botoform.plugins`` group.

The name of the `entry point`_ will be the subcommand on the CLI.

.. _function plugin:

Function plugin
===============

This example shows how to write a function plugin.

In this case we will define a ``destroy`` `entry point`_ and subcommand.

*setup.py*:

.. code-block:: python

    entry_points = {
      'botoform.plugins' : [
        'destroy = mybotoform.plugins.destroy:destroy',
      ]
    }

The `entry point`_ ``destroy`` points to the location of the function *destroy*.

The function needs to accept *args* and the *evpc* object.

*mybotoform/plugins/destroy.py*:

.. code-block:: python

 def destroy(args, evpc):
     """Destroy a VPC and related resources and services."""
     evpc.terminate()

.. _class plugin:

Class Plugin
============

If additional args and flags need to be defined, the plugin must take this form:

*setup.py*:

.. code-block:: python

    entry_points = {
      'botoform.plugins' : [
        'dump-instances = mybotoform.plugins.dump:Instances',
      ]
    }

*mybotoform/plugins/dump.py*:

.. code-block:: python

 from botoform.util import output_formatter

 class Instances(object):
     """Output a list of instance names. (example botoform plugin)"""

     @staticmethod
     def setup_parser(parser):
         parser.add_argument('--output-format',
           choices=['csv', 'yaml', 'json', 'newline'], default='newline',
           help='the desired format of any possible output')

     @staticmethod
     def main(args, evpc):
         """Output a list of instance names. (example botoform plugin)"""
         instances = evpc.instances
         print(output_formatter(map(str, instances), args.output_format))

This is a special class that has two staticmethods.

setup_parser:
 accepts subcommand parser and allows additional flags and args to be defined.

main:
 main logic for this plugin.

Terms
=====

.. _entry point:

entry point:
  An entry point is a Python object identified in a project's ``setup.py`` file.
  The object is referenced by group and name to make it discoverable.
  This means that another Python application can search the installed software.
  During the search, often the entry point group filters relevant objects.

  Botoform uses this method to allow plugins to load at run time.

