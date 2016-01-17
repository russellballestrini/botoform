
.. plugins:

plugins
#######

You may extend the :ref:`bf` tool by writing a plugin.

.. note:: For working examples see the `plugins <https://github.com/russellballestrini/botoform/tree/master/botoform/plugins>`_ directory.

A :ref:`bf` plugin must take one of two forms:

#. `function plugin`_
#. `class plugin`_

Regardless of the form of plugin you choose, your plugin project's
*setup.py* must define an `entry point`_ in the ``botoform.plugins`` group.
The name of the `entry point`_ will be the subcommand on the CLI.

All :ref:`bf` subcommands have been implemented in this way.


.. _function plugin:

function plugin
===============

This example shows how to write a `function plugin`_.

In this case we will define an `entry point`_ and subcommand named ``destroy``.

*setup.py*:

.. code-block:: python

    entry_points = {
      'botoform.plugins' : [
        'destroy = mybotoform.plugins.destroy:destroy',
      ]
    }

The `entry point`_ named ``destroy`` declares the path to the ``destroy`` function.

The function must accept an *args* object and an *evpc* object, for example:

*mybotoform/plugins/destroy.py*:

.. code-block:: python

 def destroy(args, evpc):
     """Destroy a VPC and related resources and services."""
     evpc.terminate()


.. _class plugin:

class plugin
============

This example shows how to write a `class plugin`_.

Only choose this form if your subcommand needs additional args or flags.

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


.. _core plugins:

core plugins
============

The Botoform :ref:`bf` tool ships with many core plugins and subcommands.


botoform.plugins.create
-------------------------

.. automodule:: botoform.plugins.create
    :members:
    :undoc-members:

botoform.plugins.destroy
-------------------------

.. automodule:: botoform.plugins.destroy
    :members:
    :undoc-members:


botoform.plugins.lock
-------------------------

.. automodule:: botoform.plugins.lock
    :members:
    :undoc-members:


botoform.plugins.unlock
-------------------------

.. automodule:: botoform.plugins.unlock
    :members:
    :undoc-members:


botoform.plugins.dump
-------------------------

.. automodule:: botoform.plugins.dump
    :members:
    :undoc-members:


botoform.plugins.repl
-------------------------

.. automodule:: botoform.plugins.repl
    :members:
    :undoc-members:


terms
=====

.. _entry point:

entry point:
  An entry point is a Python object identified in a project's ``setup.py`` file.
  The object is referenced by group and name to make it discoverable.
  This means that another Python application can search the installed software.
  During the search, often the entry point group filters relevant objects.

  Botoform uses this method to allow plugins to load at run time.
