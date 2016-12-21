.. _route_tables:

route_tables
############

Define route_tables using the following schema:

.. code-block:: yaml

  route_tables:
    human-readable-custom-name:
        routes:
            - ['cidr', 'destination']


Example code snippet from :download:`route_tables.yaml <../examples/route_tables.yaml>`:

.. literalinclude:: ../examples/route_tables.yaml
   :language: yaml
