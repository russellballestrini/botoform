.. _class plugin:

class plugin
############

This example shows how to write a class plugin to dump instances to STDOUT.

We show how to structure your code to define additional subparser arguments.

.. Note:: 
    Use a :ref:`function plugin` instead of a class plugin if your subcommand
    does not need to define additional flags or args.

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

