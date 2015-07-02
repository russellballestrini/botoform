Tools
#####

bf
==

All of botoform tools are namespaced under the `bf` command.

For a list subcommands and interactive help, run `bf --help`.

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
