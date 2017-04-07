Quickstart
###########

.. contents::

Installation
============

Virtualenv
------------

Both the automatic and manual install assume that the ``virtualenv`` tool is installed.
If you do not have ``virtualenv`` installed, you may do the following:

.. code-block:: bash

 # only run this if you are missing the virtualenv tool.
 sudo pip install virtualenv
 

Automatic install from source with botoform-bootstrap.sh
----------------------------------------------------------

.. Note:: You should always review scripts prior to piping them from the Internet into your shell.

This script automates the steps in the `Manual install from source`_ section.
The following one-liner will install botoform (``bf``) into your home directory:

.. code-block:: bash

 wget -O - https://raw.githubusercontent.com/russellballestrini/botoform/master/botoform-bootstrap.sh | sh
 
Once installed, you should setup your AWS `Configuration`_ file with your access keys.

You should now `Verify the botoform install`_

Manual install from source
-------------------------------

Clone botoform repo:

.. code-block:: bash

 git clone https://github.com/russellballestrini/botoform.git $HOME/botoform
 cd $HOME/botoform

Create and activate a Python virtualenv named env:
 
.. code-block:: bash

 virtualenv env
 . env/bin/activate
 

Install dependencies into virtualenv:

.. code-block:: bash

  python setup.py develop
  
You should now `Verify the botoform install`_

  
Verify the botoform install
----------------------------

Whenever you want to use the ``bf`` tool, you need to activate the virtualenv:

.. code-block::

 source $HOME/botoform/env/bin/activate

You may verify installation by running:

.. code-block:: bash

 bf --help
 

Configuration
=============

Setup your `AWS CLI config <http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html#cli-config-files>`_ file, for example -

``~/.aws/config``:

.. code-block:: bash

 [profile development]
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

