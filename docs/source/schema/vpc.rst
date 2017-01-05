.. _vpc:

vpc
#######

Optional ``vpc`` schema settings:

.. code-block:: yaml

  vpc_cidr: the-cidr-block-to-allocate-to-your-vpc
  vpc_tenancy: whether-or-not-your-vpc-should-use-default-or-dedicated 

For example:

.. code-block:: yaml

  vpc_cidr: 10.10.10.0/24
  vpc_tenancy: default

