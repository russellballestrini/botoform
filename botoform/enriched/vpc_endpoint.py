from nested_lookup import nested_lookup

from botoform.util import get_ids

class EnrichedVpcEndpoint(object):

    def __init__(self, evpc):
        self.evpc = evpc

    def describe_related(self):
        """Return VPC endpoint descriptions related to this VPC."""
        _filter = [ { 'Name' : 'vpc-id', 'Values' : [ self.evpc.id ] } ]
        return self.evpc.boto.ec2_client.describe_vpc_endpoints(Filters = _filter)

    def related_ids(self):
        """Return VPC endpoint ids related to this VPC."""
        return nested_lookup('VpcEndpointId', self.describe_related())

    def services(self):
        """Return a list of available VPC endpoint services."""
        return nested_lookup(
            'ServiceNames',
            self.evpc.boto.ec2_client.describe_vpc_endpoint_services()
        )[0]

    def create_all(self, route_table_names):
        """Accept route table names, create all endpoints for route tables."""
        route_tables = map(self.evpc.get_route_table, route_table_names)
        for endpoint in self.services():
            self.evpc.boto.ec2_client.create_vpc_endpoint(
              VpcId = self.evpc.id,
              ServiceName = endpoint,
              RouteTableIds = get_ids(route_tables),
              #PolicyDocument = 'string',
              #ClientToken = 'string'
            )

    def delete_related(self):
        """Delete all VPC endpoinds related to this VPC."""
        return self.evpc.boto.ec2_client.delete_vpc_endpoints(
            VpcEndpointIds = self.related_ids()
        )
