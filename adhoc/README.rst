Ad-hoc botoform scripts
#######################

Sometimes you need to fix an issue with AWS using programming.

Botoform may be used to quickly gather information, test a hypothesis, and fix issues.

These scripts are ad-hoc in nature but were useful to really fix an AWS account.

These scripts are committed not because they are general purpose but
because they serve as reference for building other ad-hoc scripts.

You're welcome.

Orphan ECS Services
=======================

`01_cloudformation_cleanup.py <https://github.com/russellballestrini/botoform/blob/master/adhoc/01_cloudformation_cleanup.py>`_

::

 bf -p prod exec stage < adhoc/01_cloudformation_cleanup.py

In this scenario our stage AWS ECS Cluster has a bunch of orphan ECS Services
running which are no longer controlled by CloudFormation.

We cleaned up a few of the orphans and have scaled up the cluster
from 20 -> 40 EC2 instances but it's obvious that we have a lot more
cleaning up do to.

As a result I propose we write a script to "query" CloudFormation
for all stacks. Filter stacks to just stage using tags and gather
a list of "connected" ECS Service ARNs which should be running.

Next we collect all ECS Service ARNs running in stage and we
use set theory to get the difference between reality and what we
desire in CloudFormation.

Using this new list of orphaned ARNS, we now have a list of targets
we may iterate over and destory.

We can stop and verify before proceeding with each step.
