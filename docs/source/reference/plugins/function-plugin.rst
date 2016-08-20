
.. _function plugin:

function plugin
###############

This example shows how to write a function plugin for destroying VPCs.

First we define an :ref:`entry point` and subcommand named ``destroy``.

*setup.py*:

.. code-block:: python

    entry_points = {
      'botoform.plugins' : [
        'destroy = mybotoform.plugins.destroy:destroy',
      ]
    }

The :ref:`entry point` named ``destroy`` shows the path to the ``destroy`` function.

:ref:`bf` function plugins must accept an *args* object and an *evpc* object.

For Example:

*mybotoform/plugins/destroy.py*:

.. code-block:: python

 def destroy(args, evpc):
     """
     Destroy a VPC and related resources and services.

     :param args: The parsed arguments and flags from the CLI.
     :param evpc: An instance of :meth:`botoform.enriched.vpc.EnrichedVPC`.

     :returns: None
     """
     evpc.terminate()

