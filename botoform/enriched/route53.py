from ..util import (
  reflect_attrs,
  update_tags,
  generate_password,
)

class EnrichedRoute53(object):

    def __init__(self, evpc):
        # save the EnrichedVpc object.
        self.evpc = evpc

        # capture a list of this classes attributes before reflecting.
        self.self_attrs = dir(self)

        # reflect all connection attributes into EnrichedElb.
        reflect_attrs(self, self.evpc.boto.route53, self.self_attrs)

    @property
    def private_zone_name(self):
        return "{}.local.".format(self.evpc.name)

    @property
    def private_zone_id(self):
        """get the vpc with the private hosted zone id from vpc tag."""
        return self.evpc.tag_dict.get('private_hosted_zone_id', None)

    @private_zone_id.setter
    def private_zone_id(self, new_id):
        """tag the vpc with the private hosted zone id for future reference."""
        new_id = new_id if new_id else ''
        update_tags(self.evpc, private_hosted_zone_id = new_id)
        self.evpc.reload()

    def create_private_zone(self):
        if self.private_zone_id: return None
        comment = 'private zone for {}'.format(self.evpc.name)
        response = self.create_hosted_zone(
            Name = self.private_zone_name,
            VPC  = { 'VPCRegion' : self.evpc.region_name, 'VPCId' : self.evpc.id },
            HostedZoneConfig = { 'Comment': comment, 'PrivateZone': True },
            CallerReference = generate_password()
        )

        # response id is like '/hostedzone/xjwurixi'
        self.private_zone_id = response['HostedZone']['Id'].split('/')[-1]

    def change_private_zone(self, change_docs):
        self.change_resource_record_sets(
            HostedZoneId = self.private_zone_id,
            ChangeBatch={
              'Changes': change_docs,
            }
        )

    def empty_private_zone(self):
        if not self.private_zone_id: return None
        response = self.list_resource_record_sets(HostedZoneId = self.private_zone_id)
        record_sets = response['ResourceRecordSets']
        change_docs = []
        for record_set in record_sets:
            change_doc = {}
            change_doc['Action'] = 'DELETE'
            change_doc['ResourceRecordSet'] = record_set
            if record_set['Type'] not in ['NS', 'SOA']:
                # only add the change_doc if its _not_ an NS or SOA record.
                change_docs.append(change_doc)

        if len(change_docs) != 0:
            self.change_private_zone(change_docs)

    def delete_private_zone(self):
        if not self.private_zone_id: return None
        self.empty_private_zone()
        try:
            self.delete_hosted_zone(Id = self.private_zone_id)
        except:
            return None

    def refresh_private_zone(self):
        if not self.private_zone_id: return None
        instance_change_docs = [self._ipcd(i) for i in self.evpc.instances]
        role_change_docs = [self._rpcd(role_name, instances) for role_name, instances in self.evpc.roles.items()]
        change_docs = instance_change_docs + role_change_docs
        self.change_private_zone(change_docs)

    def _ipcd(self, instance):
        """return private change doc for an instance."""
        return self._pcd(instance.hostname, [instance.private_ip_address])

    def _rpcd(self, role_name, instances=None):
        """return private change doc for a role."""
        if instances is None:
            instances = evpc.get_role(role_name)
        # route53 limits to 100 per resource record set, we slice to this limit.
        #  reference: http://docs.aws.amazon.com/Route53/latest/DeveloperGuide/DNSLimitations.html#limits-api-entities
        return self._pcd(role_name, [instance.private_ip_address for instance in instances[:100]])

    def _pcd(self, hostname, private_ip_addresses):
        """
        Generate a private change doc for the private zone.

        :param hostname: hostname part of the DNS A record
        :param private_ip_addresses: list of private ip addresses

        :returns: dict (change document)
        """
        change_doc = {
                 'Action': 'UPSERT',
                 'ResourceRecordSet': {
                   'Name': '{}.{}'.format(hostname, self.private_zone_name),
                   'Type': 'A',
                   'TTL': 120,
                   'ResourceRecords': [],
                 }
               }
        for private_ip_address in private_ip_addresses:
            change_doc['ResourceRecordSet']['ResourceRecords'].append({'Value': private_ip_address})
        return change_doc

