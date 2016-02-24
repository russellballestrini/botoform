Botoform
########

**Architect infrastructure on AWS using YAML.**

.. contents:: 

Botoform_ provides tools to manage the lifecycle of related AWS resources.
We use a simple YAML schema to document resources and infrastructure.
The YAML schema has self documenting qualities and works with version control.

The tools use the YAML architecture to create and manage environments.
Botoform_ allows reproduction of any environment, no matter how complex.

Botoform_ abstracts and enriches the Boto3_ and Botocore_ projects.

Documentation
=============

We use Sphinx_ and host the full documentation at botoform.readthedocs.org_. 

Quickstart
------------------

The `Quickstart Guide`_ will teach you how to setup your aws credential config file
and create and destroy a real test VPC using botoform.

Schema Reference
------------------

The full YAML Schema_ Reference documentation is in progress.

For now please look here for examples:

https://github.com/russellballestrini/botoform/blob/master/tests/fixtures/webapp.yaml


Misc
====

What about CloudFormation?
 I couldn't figure out how to use CloudFormation and I think that is a problem... 
 Botoform will not support all the things that CloudFormation does, and at times it will be opinionated to keep things simple, usable, and understandable. 
 
What about Terraform?
 Terraform focuses on many different cloud providers, and uses hashicorp configuration language.
 Botoform will focus only on AWS, and uses YAML + Jinja2 configuration.
 Ideally Botoform will be easier to use and more feature/service complete then Terraform for AWS.
 
.. _Botoform: http://botoform.com
.. _Botocore: http://botocore.com
.. _Boto3: http://boto3.com
.. _Sphinx: https://github.com/russellballestrini/botoform/tree/master/docs#sphinx
.. _Quickstart Guide: https://botoform.readthedocs.org/en/latest/guides/quickstart.html
.. _Schema: https://botoform.readthedocs.org/en/latest/schema/index.html
.. _botoform.readthedocs.org: https://botoform.readthedocs.org/
