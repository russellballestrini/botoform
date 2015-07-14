Extending bf
############

You may extend the ``bf`` tool by writing a plugin.

``bf`` plugins come in two forms: `function plugin`_ or `class plugin`_

We write all ``bf`` subcommands in this way, so there are plenty of examples.

Create an entry_point in your *setup.py* in the botoform.plugins group.
The *entry_point* may point to a function or a special plugin class.

.. _function plugin:

function plugin
===============

*setup.py*:

.. code-block:: python

    entry_points = {
      'botoform.plugins' : [
        'dump-instances = botoform.plugins.dump:dump_instances',
      ]
    }

The name of the entry_point will be the name of the subcommand on the CLI.

In this case the entry_point / subcommand name will be ``dump-instances``.

``dump-instances`` points to the location of the function *dump_instances*.

The function needs to accept *args* and the *evpc* object.

.. code-block:: python

 def dump_instances(args, evpc):
     """Dump instances (This docstring is used in the subcommand help)"""
     for instance in evpc.instances:
         print(instance)

.. _class plugin:

class plugin
============

If additional args and flags need to be defined, our plugin must take this form:

*setup.py*:

.. code-block:: python

    entry_points = {
      'botoform.plugins' : [
        'dump-instances = botoform.plugins.dump:Instances',
      ]
    }

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

