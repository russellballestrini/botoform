.. _subnets:

subnets
#######

Define subnets using the following schema:

.. code-block:: yaml

  subnets:

    human-readable-custom-name:

        size: cidr_integer
        route_table: name-of-the-route-table
        description: human readable description (optional)
        availability_zone: char of az (optional)

Example code snippet from :download:`subnets.yaml <../examples/subnets.yaml>`:

.. literalinclude:: ../examples/subnets.yaml
   :language: yaml
