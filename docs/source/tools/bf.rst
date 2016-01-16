.. _bf:

bf
##

All of botoform tools are namespaced under the `bf` command.

For a list built-in subcommands and interactive help, run `bf --help`.

create
------

Create a new VPC and related services, modeled after the given YAML template.

For example:

.. code-block:: bash

 bf create dogtest01 192.168.1.0/24 tests/fixtures/webapp.yaml

destroy
-------

.. warning:: this is destructive!

Destroy a VPC and all related services.

For example:

.. code-block:: bash

 bf destroy dogtest01

refresh
-------

.. note:: not implemented yet.

Refresh VPC by adding resources defined but missing in given YAML template.

* instances
* security groups
* security group rules
* rds database instances
* elasticache clusters
* load balancers


reflect
-------

.. note:: not implemented yet.

.. warning:: this is destructive!

Make VPC reflect given YAML template by adding and removing resources.

* instances
* security groups
* security group rules
* rds database instances
* elasticache clusters
* load balancers

stop
-------

.. note:: not implemented yet.

Stop all instances in VPC including autoscaled instances.

TODO: Skip "ephemeral" instances!

start
-------

.. note:: not implemented yet.

Start all instances in VPC including autoscaled instances.

lock
-------

.. note:: not implemented yet.

Enable API Termination Protection on all instances in VPC.

unlock
-------

.. note:: not implemented yet.

Disable API Termination Protection on all instances in VPC.

tag
-------

.. note:: not implemented yet.

Tag all ec2objects with given tags.

untag
-------

.. note:: not implemented yet.

Untag all ec2objects with given tags.


.. _repl:

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

* instances
* security-groups


