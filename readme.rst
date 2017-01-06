Botoform
########

**Architect infrastructure on AWS using YAML.**

Botoform_ provides tools to manage the lifecycle of related AWS resources.
We use a simple YAML schema to document resources and infrastructure.
The YAML schema has self documenting qualities and works with version control.

In this example we use the ``bf create`` tool to build
the infrastructure defined in ``helloworld.yaml``:

.. image:: https://raw.githubusercontent.com/russellballestrini/botoform/master/docs/source/_static/botoform-helloworld.gif

The ``bf`` tools use the YAML architecture to create and manage environments.
Botoform_ allows reproduction of any environment, no matter how complex.

Botoform_ abstracts and enriches the Boto3_ and Botocore_ projects.


Documentation
=============

The full documentation lives here: botoform.readthedocs.org_

We use Sphinx_ to write and build the documentation.

Quickstart
------------------

The `Quickstart Guide`_ will teach you how to setup your aws credential config file
and create and destroy a real test VPC using botoform.

helloworld.yaml
------------------

Here we show a small example of what botoform can do.

This will build a VPC, Internet Gateway, Route table, Subnet, Security Group, and a single EC2 instance.

.. code-block:: yaml

 vpc_cidr: {{ vpc_cidr }}

 amis:
   ubuntu-14.04-lts-hvm:
     us-east-1: ami-fce3c696

 route_tables:
   public:
     routes:
       - ['0.0.0.0/0', 'internet_gateway']

 subnets:
   public-1: 
     size: 27
     route_table: public
     public: True

 security_groups:
   bastion:
     inbound:
       - ['0.0.0.0/0', 'tcp',   22]

 instance_roles:
   bastion:
     instance_type: t2.micro
     ami: 'ubuntu-14.04-lts-hvm'
     count: 1
     security_groups: ['bastion']
     subnets: ['public-1']
     eip: true
     block_devices:
       "/dev/sda1":
         size: 10


Schema Reference
------------------

The full YAML Schema_ Reference documentation is in progress.

For now please look here for examples:

 https://github.com/russellballestrini/botoform/blob/master/tests/fixtures/webapp.yaml

You may optionally use Jinja2 in your YAML config.

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
