Quickstart
###########

.. contents::

Installation
============

Install from source.

Clone botoform repo:

.. code-block:: bash

 git clone https://github.com/russellballestrini/botoform.git
 cd botoform

Create and activate a Python virtualenv named env:

.. code-block:: bash

 virtualenv env
 . env/bin/activate

Install dependencies into virtualenv:

.. code-block:: bash

  python setup.py develop

Verify installation by running:

.. code-block:: bash

 bf --help
 

Configuration
=============

Setup your `AWS CLI config <http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html#cli-config-files>`_ file, for example:

.. code-block:: bash

 [development]
 aws_access_key_id = AKIAIOSFODNN7EXAMPLE
 aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
 region = us-west-2

Using Botoform
==============


Create VPC
-------------

.. Note:: This section will create real resources on AWS.

.. code-block:: bash

 bf --profile=development --region=ap-southeast-1 create dogtest01 192.168.1.0/24 tests/fixtures/webapp.yaml
    

Unlock VPC
-------------

.. Note:: This command will unlock instances to allow them to be terminated.

Disable API Termination Protection on all instances in VPC.

.. code-block:: bash

 bf --profile=development --region=ap-southeast-1 unlock dogtest01


Destroy VPC
-------------

.. Danger:: This command will completely destroy the entire VPC and all related resources!

.. code-block:: bash
  
 bf --profile=development --region=ap-southeast-1 destroy dogtest01

Example Output
==============

.. code-block:: bash

 bf --profile=development --region=ap-southeast-1 create dogtest01 192.168.1.1/24 tests/fixtures/webapp.yaml
 creating vpc (dogtest01, 192.168.1.1/24)
 tagging vpc (Name:dogtest01)
 modifying vpc for dns support
 modifying vpc for dns hostnames
 creating internet_gateway (igw-dogtest01)
 tagging gateway (Name:igw-dogtest01)
 attaching igw to vpc (igw-dogtest01)
 creating route_table (dogtest01-public)
 tagging route_table (Name:dogtest01-public)
 adding route ['0.0.0.0/0', 'internet_gateway'] to route_table (dogtest01-public)
 creating route_table (dogtest01-private)
 tagging route_table (Name:dogtest01-private)
 creating subnet 192.168.1.96/27 in ap-southeast-1b
 tagging subnet (Name:dogtest01-private-2)
 creating subnet 192.168.1.64/27 in ap-southeast-1a
 tagging subnet (Name:dogtest01-private-1)
 creating subnet 192.168.1.32/27 in ap-southeast-1a
 tagging subnet (Name:dogtest01-public-1)
 creating subnet 192.168.1.0/27 in ap-southeast-1b
 tagging subnet (Name:dogtest01-public-2)
 associating rt private with sn private-2
 associating rt private with sn private-1
 associating rt public with sn public-1
 associating rt public with sn public-2
 creating security_group dogtest01-db
 tagging security_group (Name:dogtest01-db)
 creating security_group dogtest01-web
 tagging security_group (Name:dogtest01-web)
 creating security_group dogtest01-door
 tagging security_group (Name:dogtest01-door)
 creating security_group dogtest01-web-elb
 tagging security_group (Name:dogtest01-web-elb)
 creating key pair door
 creating key pair default
 creating role: db
 1 instances of role db launching into dogtest01-private-1
 tagging instance i-1427479a (Name:dogtest01-db-1427479a, role:db)
 creating role: web
 1 instances of role web launching into dogtest01-private-2
 1 instances of role web launching into dogtest01-private-1
 tagging instance i-a1b7f505 (Name:dogtest01-web-a1b7f505, role:web)
 tagging instance i-7a2848f4 (Name:dogtest01-web-7a2848f4, role:web)
 creating role: door
 1 instances of role door launching into dogtest01-public-1
 tagging instance i-16284898 (Name:dogtest01-door-16284898, role:door)
 creating vpc endpoints in private
 'web' into 'db' over ports 5432 (TCP)
 'door' into 'db' over ports 22 (TCP)
 'web-elb' into 'web' over ports 80 (TCP)
 'door' into 'web' over ports 22 (TCP)
 '0.0.0.0/0' into 'door' over ports 22 (TCP)
 '0.0.0.0/0' into 'web-elb' over ports 80 (TCP)
 waiting for dogtest01-db-1427479a to start
 tagging volumes for instance dogtest01-db-1427479a (Name:dogtest01-db-1427479a)
 waiting for dogtest01-web-a1b7f505 to start
 tagging volumes for instance dogtest01-web-a1b7f505 (Name:dogtest01-web-a1b7f505)
 waiting for dogtest01-web-7a2848f4 to start
 tagging volumes for instance dogtest01-web-7a2848f4 (Name:dogtest01-web-7a2848f4)
 waiting for dogtest01-door-16284898 to start
 tagging volumes for instance dogtest01-door-16284898 (Name:dogtest01-door-16284898)
 allocating eip and associating with dogtest01-door-16284898
 allocated eip 52.76.204.99 and associated with dogtest01-door-16284898
 locking new instances to prevent termination
 done! don't you look awesome. : )
