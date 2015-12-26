Botoform
########

**Manage infrastructure running on AWS using YAML templates.**

Botoform_ provides tools to manage the lifecycle of related AWS resources.
We use a simple YAML schema to document resources as infrastructure.
The YAML schema has self documenting qualities and works with version control.

The tools use the YAML architecture to create and manage environments.
Botoform_ allows reproduction of any environment, no matter how complex.

Botoform_ abstracts and enriches the Boto3_ and Botocore_ projects.

Quickstart
=============

Quickstart_ 

Documentation
=============

We use Sphinx_ and https://botoform.readthedocs.org/

YAML Schema
=============

I didn't write the docs for the YAML schema yet, but here is an example:

https://github.com/russellballestrini/botoform/blob/master/tests/fixtures/webapp.yaml

Misc
====

What about CloudFormation?
 I couldn't figure out how to use CloudFormation and I think that is a problem... 
 Botoform will not support all the things that CloudFormation does, and at times it will be opionionated to keep things simple, usable, and understandable. 

.. _Botoform: http://botoform.com
.. _Botocore: http://botocore.com
.. _Boto3: http://boto3.com
.. _Sphinx: https://github.com/russellballestrini/botoform/tree/master/docs
.. _Quickstart: https://botoform.readthedocs.org/en/latest/guides/quickstart.html
