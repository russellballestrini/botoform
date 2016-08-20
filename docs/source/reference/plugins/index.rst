
plugins
#######

You may extend the :ref:`bf` tool by writing a plugin.

A :ref:`bf` plugin must take one of two forms:

.. toctree::
   :maxdepth: 2

   function-plugin.rst
   class-plugin.rst

Regardless of the form of plugin you choose, your plugin project's
*setup.py* must define an :ref:`entry point` in the ``botoform.plugins`` group.
The name of the :ref:`entry point` will be the subcommand on the CLI.

All :ref:`bf` subcommands (:ref:`core plugins`) are implemented in this way.

.. seealso:: working examples `plugins <https://github.com/russellballestrini/botoform/tree/master/botoform/plugins>`_ directory.

core plugins
============

.. toctree::
   :maxdepth: 2

   core-plugins.rst

terms
=====

.. _entry point:

entry point
-----------

entry point:
  An entry point is a Python object identified in a project's ``setup.py`` file.
  The object is referenced by group and name to make it discoverable.

  This means that another Python application can search for installed software.
  During the search, often the entry point group filters relevant objects.

  Botoform uses this method to allow plugins to load at run time.
