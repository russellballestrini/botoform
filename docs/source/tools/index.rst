Tools
#####

bf
==

All of botoform tools are namespaced under the `bf` command.

For a list built-in subcommands and interactive help, run `bf --help`.

create
------

Create a new VPC and related services, modeled after the given YAML template.

destroy
-------

.. warning:: this is destructive!

Destroy a VPC and all related services.

refresh
-------

Refresh VPC by adding "things" defined but missing in given YAML template.

* instances
* security groups
* security group rules
* rds database instances
* elasticache clusters
* load balancers


reflect
-------

.. warning:: this is destructive!

Make VPC reflect given YAML template by adding and removing "things".

* instances
* security groups
* security group rules
* rds database instances
* elasticache clusters
* load balancers

stop
-------

Stop all instances in VPC including autoscaled instances.

TODO: Skip "ephemeral" instances!

start
-------

Start all instances in VPC including autoscaled instances.

lock
-------

Enable API Termination Protection on all instances in VPC.

unlock
-------

Disable API Termination Protection on all instances in VPC.

tag
-------

Tag all ec2objects with given tags.

untag
-------

Untag all ec2objects with given tags.

repl
----

Open an interactive REPL (read-eval-print-loop) with access to evpc object.

Once you have a shell, try running *evpc.roles* or *evpc.instances*.

.. code-block:: bash

 usage: bf vpc_name repl [-h]

Note:
 Install *bpython* into your environment for more fun.

.. code-block:: bash

 bf webapp01 repl

 You now have access to the evpc object, for example: evpc.roles

 >>> evpc.instances
 [<botoform.evpc.instance.EnrichedInstance object at 0x10e3346d0>,
 <botoform.evpc.instance.EnrichedInstance object at 0x10c9b9190>]

 >>> map(str, evpc.instances)
 ['webapp01-web01', 'webapp01-web02']

dump-instances
--------------

Dump instance names in various ways...

This is mostly an example for how to write a botoform plugin.


dump-security-groups
--------------------

Dump Security Groups in a format that is compatible with Botoform templates.


