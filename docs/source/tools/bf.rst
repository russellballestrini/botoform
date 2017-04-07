.. _bf:

bf
##

Botoform tools are namespaced under the ``bf`` command.

For a list built-in subcommands and interactive help, run ``bf --help``.

Currently Implemented subcommands::

 {atmosphere,shell,cli,dump,list,lock,create,stop,start,unlock,repl,destroy}

.. _bf list:

list
------

List all existing VPC names.

For example:

.. code-block:: bash

 bf list

You can also pass the particular AWS profile and/or region:

.. code-block:: bash

 bf --profile developmemt --region us-west-2 list

.. _bf create:

create
------

Create a new VPC and related services, modeled after the given YAML template.

For example:

.. code-block:: bash

 bf create dogtest01 -e 'vpc_cidr=192.168.1.0/24' tests/fixtures/webapp.yaml

destroy
-------

.. warning:: this is destructive!

Destroy a VPC and all related services.

For example:

.. code-block:: bash

 bf destroy dogtest01

refresh
-------

Refresh VPC by adding resources defined but missing in given YAML template.

So far we have implemented the following subcommands:

* ``instance_roles``
* ``security_groups``
* ``load_balacers``
* ``tags``
* ``private_zone``


reflect
-------

.. note:: not implemented yet.

.. warning:: this is destructive!

Make VPC reflect given YAML template by adding and removing resources.

* ``instance_roles``
* ``security_groups``
* ``tags``
* ``private_zone``


stop
-------

Stop all instances in VPC including autoscaled instances.

.. warning:: Currently does _NOT_ skip "ephemeral" instances!

start
-------

Start all instances in VPC including autoscaled instances.

lock
-------

Enable API Termination Protection on all instances in VPC.

unlock
-------

Disable API Termination Protection on all instances in VPC.

repl
-----

Open an interactive REPL (read-eval-print-loop) with access to evpc object.

Once you have a repl, try running *evpc.roles* or *evpc.instances*.

.. code-block:: bash

 usage: bf repl vpc_name  [-h]

Note:
 Install *bpython* into your environment for more fun.

.. code-block:: bash

 bf webapp01 repl

 You now have access to the evpc object, for example: evpc.roles

 >>> evpc.instances
 [<botoform.enriched.instance.EnrichedInstance object at 0x10e194350>,
 <botoform.enriched.instance.EnrichedInstance object at 0x10e1944d0>

 >>> map(str, evpc.instances)
 ['webapp01-web01', 'webapp01-web02']


cli
---

An alias to repl_ so it works the same.

shell
-----

An alias to repl_ so it works the same.

dump
----

Output existing resources or services in a Botoform campatible format.

* ``instances``
* ``security_groups``
* ``ansible_hosts``
* ``tags``


atmosphere
-----------

For every AWS profile + region, dump every VPC to STDOUT.

This command takes a while to run, so you should likely redirect the output to a file.

Reason for this tool is we have many AWS accounts and we use many regions.

Using the output of this tool, we can easily grep for a vpc_name and find where it lives.
