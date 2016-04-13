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

 bf --profile=development --region=ap-southeast-1 create dogtest01 -e 'vpc_cidr=192.168.1.0/24' tests/fixtures/webapp.yaml
    

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

.. literalinclude:: ../examples/bf-output.txt
   :language: bash

