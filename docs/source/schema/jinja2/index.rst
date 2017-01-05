.. _jinja2:

Jinja2
###########

Jinja2 is a templating language.

.. note:: Jinja2 is optional and considered "advanced".

Jinja2 variable substitutions
================================

One popular use of Jinja2 is for variable substitutions and expansions.

In this example we use a substitution to define the ``vpc_cidr``.

.. code-block:: yaml

  vpc_cidr: {{ vpc_cidr }}

When the time comes to create a new VPC, we pass an extra variable using ``-e``.

For example, to set the ``vpc_cidr`` to ``192.168.1.0/24``:

.. code-block:: bash

 bf create dogtest01 -e 'vpc_cidr=192.168.1.0/24' webapp.yaml

Jinja2 default filter
================================

In this example we will use a Jinja2 filter called ``default``.

Like our example from before, but this time setting a default.

.. code-block:: yaml

  vpc_cidr: {{ vpc_cidr | default(10.10.0.0/24) }}

Now the user may omit the extra variables and we will use the default.
