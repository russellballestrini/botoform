import traceback

from botoform.enriched import EnrichedVPC

from botoform.util import (
  BotoConnections,
  Log,
  update_tags,
  make_tag_dict,
  get_port_range,
  get_ids,
  collection_len,
  generate_password,
)

from botoform.subnetallocator import allocate

from uuid import uuid4

class EnvironmentBuilder(object):

    def __init__(self, vpc_name, config=None, region_name=None, profile_name=None, log=None):
        """
        vpc_name:
         The human readable Name tag of this VPC.

        config:
         The dict returned by botoform.config.ConfigLoader's load method.
        """
        self.vpc_name = vpc_name
        self.config = config if config is not None else {}
        self.log = log if log is not None else Log()
        self.boto = BotoConnections(region_name, profile_name)
        self.reflect = False

    def apply_all(self):
        """Build the environment specified in the config."""
        try:
            self._apply_all(self.config)
        except Exception as e:
            self.log.emit('Botoform failed to build environment!', 'error')
            self.log.emit('Failure reason: {}'.format(e), 'error')
            self.log.emit(traceback.format_exc(), 'debug')
            self.log.emit('Tearing down failed environment!', 'error')
            self.evpc.terminate()
            raise

    def _apply_all(self, config):

        # Make sure amis is setup early. (TODO: raise exception if missing)
        self.amis = config['amis']

        # set a var for no_cfg.
        no_cfg = {}

        # builds the vpc.
        self.build_vpc(config.get('vpc_cidr', None))

        # attach EnrichedVPC to self.
        self.evpc = EnrichedVPC(self.vpc_name, self.boto.region_name, self.boto.profile_name, self.log)

        # attach VPN gateway to the VPC
        self.attach_vpn_gateway(config.get('vpn_gateway', no_cfg))
        
        # create and associate DHCP Options Set
        self.dhcp_options(config.get('dhcp_options', no_cfg))
        
        # the order of these method calls matters for new VPCs.
        self.route_tables(config.get('route_tables', no_cfg))
        self.subnets(config.get('subnets', no_cfg))
        self.associate_route_tables_with_subnets(config.get('subnets', no_cfg))
        self.security_groups(config.get('security_groups', no_cfg))
        self.key_pairs(config.get('key_pairs', []))
        self.db_instances(config.get('db_instances', no_cfg))
        new_instances = self.instance_roles(
            config.get('instance_roles', no_cfg)
        )
        # lets do more work while new_instances move from pending to running.
        self.endpoints(config.get('endpoints', []))
        self.security_group_rules(config.get('security_groups', no_cfg))
        self.load_balancers(config.get('load_balancers', no_cfg))
        # lets finish building the new instances.
        self.finish_instance_roles(
            config.get('instance_roles', no_cfg), new_instances,
        )
        self.log.emit('done! don\'t you look awesome. : )')

    def build_vpc(self, cidrblock):
        """Build VPC"""
        self.log.emit('creating vpc ({}, {})'.format(self.vpc_name, cidrblock))
        vpc = self.boto.ec2.create_vpc(CidrBlock = cidrblock)

        self.log.emit('tagging vpc (Name:{})'.format(self.vpc_name), 'debug')
        update_tags(vpc, Name = self.vpc_name)

        self.log.emit('modifying vpc for dns support', 'debug')
        vpc.modify_attribute(EnableDnsSupport={'Value': True})
        self.log.emit('modifying vpc for dns hostnames', 'debug')
        vpc.modify_attribute(EnableDnsHostnames={'Value': True})

        igw_name = 'igw-' + self.vpc_name
        self.log.emit('creating internet_gateway ({})'.format(igw_name))
        gw = self.boto.ec2.create_internet_gateway()
        self.log.emit('tagging gateway (Name:{})'.format(igw_name), 'debug')
        update_tags(gw, Name = igw_name)

        self.log.emit('attaching igw to vpc ({})'.format(igw_name))
        vpc.attach_internet_gateway(
            DryRun=False,
            InternetGatewayId=gw.id,
            VpcId=vpc.id,
        )

    def attach_vpn_gateway(self, vpn_gateway_cfg):
        """Attach defined VPN gateway to VPC"""
        if vpn_gateway_cfg:
            vgw_id = vpn_gateway_cfg.get('id', None)
            if vgw_id is not None:
                self.log.emit('attaching vgw ({}) to vpc ({})'.format(vgw_id, self.vpc_name))
                # attach_vpn_gateway is available with ec2 client object
                self.evpc.attach_vpn_gateway(vgw_id)
                #self.vgw_id = vgw_id
                #self.boto.ec2_client.attach_vpn_gateway(
                #    DryRun=False,
                #    VpnGatewayId = self.vgw_id,
                #    VpcId = self.evpc.id,
                #)
                ## check & wait till VGW (2 min.) is attached
                #count = 0
                #while(not self.evpc.is_vgw_attached(vgw_id)):
                #    time.sleep(10)
                #    count += 1
                #    if count == 11:
                #        raise Exception({"message":"VPN Gateway is not yet attached.", "VGW_ID":vgw_id})

    def dhcp_options(self, dhcp_options_cfg):
        """Creates DHCP Options Set and associates with VPC"""
        for dhcp_name, data in dhcp_options_cfg.items():
            longname = '{}-{}'.format(self.evpc.name, dhcp_name)
            self.log.emit('creating DHCP Options Set {}'.format(longname))
            dhcp_options_id = self.evpc.create_dhcp_options(data)
            # associate DHCP Options with VPC
            self.log.emit('associating DHCP Options {} ({}) with VPC {}'.format(longname, dhcp_options_id, self.vpc_name))
            self.evpc.associate_dhcp_options(
                DhcpOptionsId=dhcp_options_id
            )
            self.evpc.reload()
            update_tags(self.evpc.dhcp_options, Name=longname)
        
    def route_tables(self, route_cfg):
        """Build route_tables defined in config"""
        for rt_name, data in route_cfg.items():
            longname = '{}-{}'.format(self.evpc.name, rt_name)
            route_table = self.evpc.get_route_table(longname)
            if route_table is None:
                self.log.emit('creating route_table ({})'.format(longname))
                if data.get('main', False) == True:
                    route_table = self.evpc.get_main_route_table()
                else:
                    route_table = self.evpc.create_route_table()
                self.log.emit('tagging route_table (Name:{})'.format(longname), 'debug')
                update_tags(route_table, Name = longname)

            # TODO: move to separate method ...
            #   gatewayId, natGatewayId, networkInterfaceId,
            #   vpcPeeringConnectionId or instanceId
            #   add routes to route_table defined in configuration.
            for route in data.get('routes', []):
                destination, target = route
                self.log.emit('adding route {} to route_table ({})'.format(route, longname))
                if target.lower() == 'internet_gateway':
                    # TODO: ugly but we assume only one internet gateway.
                    route_table.create_route(
                        DestinationCidrBlock = destination,
                        GatewayId = list(self.evpc.internet_gateways.all())[0].id,
                    )
                if target.lower() == 'vpn_gateway':
                    # TODO: ugly but we assume only one VPN gateway.
                    route_table.create_route(
                        DestinationCidrBlock = destination,
                        GatewayId = self.evpc.vgw_id,
                    )
                    
                    # if routed to VPN gateway propagate the route.
                    self.boto.ec2_client.enable_vgw_route_propagation(
                        RouteTableId = route_table.route_table_id,
                        GatewayId = self.evpc.vgw_id,
                    )

    def subnets(self, subnet_cfg):
        """Build subnets defined in config."""
        sizes = sorted([x['size'] for x in subnet_cfg.values()])
        cidrs = allocate(self.evpc.cidr_block, sizes)

        azones = self.evpc.azones

        subnets = {}
        for size, cidr in zip(sizes, cidrs):
            subnets.setdefault(size, []).append(cidr)

        for name, sn in subnet_cfg.items():
            longname = '{}-{}'.format(self.evpc.name, name)
            az_letter = sn.get('availability_zone', None)
            if az_letter is not None:
                az_name = self.evpc.region_name + az_letter
            else:
                az_index = int(name.split('-')[-1]) - 1
                az_name = azones[az_index]

            cidr = subnets[sn['size']].pop()
            self.log.emit('creating subnet {} in {}'.format(cidr, az_name))
            subnet = self.evpc.create_subnet(
                          CidrBlock = str(cidr),
                          AvailabilityZone = az_name
            )
            self.log.emit('tagging subnet (Name:{})'.format(longname), 'debug')
            update_tags(
                subnet,
                Name = longname,
                description = sn.get('description', ''),
            )
            # Modifying the subnet's public IP addressing behavior.
            if sn.get('public', False) == True:
                subnet.map_public_ip_on_launch = True

    def associate_route_tables_with_subnets(self, subnet_cfg):
        for sn_name, sn_data in subnet_cfg.items():
            rt_name = sn_data.get('route_table', None)
            if rt_name is None:
                continue
            self.log.emit('associating rt {} with sn {}'.format(rt_name, sn_name))
            self.evpc.associate_route_table_with_subnet(rt_name, sn_name)

    def endpoints(self, route_tables):
        """Build VPC endpoints for given route_tables"""
        if len(route_tables) == 0:
            return None
        self.log.emit(
            'creating vpc endpoints in {}'.format(', '.join(route_tables))
        )
        self.evpc.vpc_endpoint.create_all(route_tables)

    def security_groups(self, security_group_cfg):
        """Build Security Groups defined in config."""

        for sg_name, rules in security_group_cfg.items():
            sg = self.evpc.get_security_group(sg_name)
            if sg is not None:
                continue
            longname = '{}-{}'.format(self.evpc.name, sg_name)
            self.log.emit('creating security_group {}'.format(longname))
            security_group = self.evpc.create_security_group(
                GroupName   = longname,
                Description = longname,
            )
            self.log.emit(
                'tagging security_group (Name:{})'.format(longname), 'debug'
            )
            update_tags(security_group, Name = longname)

    def security_group_rules(self, security_group_cfg):
        """Build Security Group Rules defined in config."""
        self.security_group_inbound_rules(security_group_cfg)
        self.security_group_outbound_rules(security_group_cfg)

    def security_group_inbound_rules(self, security_group_cfg):
        """Build inbound rule for Security Group defined in config."""
        msg = "inbound connection from '{}' to '{}' over ports {} ({})"
        for sg_name, rules in security_group_cfg.items():
            sg = self.evpc.get_security_group(sg_name)
            permissions = []
            for rule in rules.get('inbound', {}):
                protocol = rule[1]
                from_port, to_port = get_port_range(rule[2], protocol)
                src_sg = self.evpc.get_security_group(rule[0])

                permission = {
                    'IpProtocol' : protocol,
                    'FromPort'   : from_port,
                    'ToPort'     : to_port,
                }

                if src_sg is None:
                    permission['IpRanges'] = [{'CidrIp' : rule[0]}]
                else:
                    permission['UserIdGroupPairs'] = [{'GroupId':src_sg.id}]

                permissions.append(permission)

                fmsg = msg.format(rule[0],sg_name,rule[2],rule[1].upper())
                self.log.emit(fmsg)
            
            if permissions:
                sg.authorize_ingress(
                    IpPermissions = permissions
                )

    def security_group_outbound_rules(self, security_group_cfg):
        """Build outbound rule for Security Group defined in config."""
        msg = "outbound connection to '{}' from '{}' over ports {} ({})"
        for sg_name, rules in security_group_cfg.items():
            sg = self.evpc.get_security_group(sg_name)

            permissions = []
            for rule in rules.get('outbound', {}):

                self.log.emit("revoking default outbound rule from {}".format(sg_name))
                sg.revoke_egress(
                  IpPermissions = [
                    {
                      'IpProtocol' : '-1',
                      'FromPort'   : -1,
                      'ToPort'     : -1,
                      'IpRanges'   : [ { 'CidrIp' : '0.0.0.0/0' } ],
                    }
                  ]
                )

                protocol = rule[1]
                from_port, to_port = get_port_range(rule[2], protocol)
                src_sg = self.evpc.get_security_group(rule[0])

                permission = {
                    'IpProtocol' : protocol,
                    'FromPort'   : from_port,
                    'ToPort'     : to_port,
                }

                if src_sg is None:
                    permission['IpRanges'] = [{'CidrIp' : rule[0]}]
                else:
                    permission['UserIdGroupPairs'] = [{'GroupId':src_sg.id}]

                permissions.append(permission)

                fmsg = msg.format(rule[0],sg_name,rule[2],rule[1].upper())
                self.log.emit(fmsg)
            
            if permissions:
                sg.authorize_egress(
                    IpPermissions = permissions
                )

    def key_pairs(self, key_pair_cfg):
        key_pair_cfg.append('default')
        for short_key_pair_name in key_pair_cfg:
            if self.evpc.key_pair.get_key_pair(short_key_pair_name) is None:
                self.log.emit('creating key pair {}'.format(short_key_pair_name))
                self.evpc.key_pair.create_key_pair(short_key_pair_name)

    def instance_roles(self, instance_role_cfg):
        """Returns a list of new created EnrichedInstance objects."""
        new_instances = []
        for role_name, role_data in instance_role_cfg.items():
            desired_count = role_data.get('count', 0)
            role_instances = self.instance_role(
                                 role_name,
                                 role_data,
                                 desired_count,
                             )
            new_instances += role_instances
        return new_instances

    def instance_role(self, role_name, role_data, desired_count):
        self.log.emit('creating role: {}'.format(role_name))
        ami = self.amis[role_data['ami']][self.evpc.region_name]

        key_pair = self.evpc.key_pair.get_key_pair(
                       role_data.get('key_pair', 'default')
                   )

        security_groups = map(
            self.evpc.get_security_group,
            role_data.get('security_groups', [])
        )

        subnets = map(
            self.evpc.get_subnet,
            role_data.get('subnets', [])
        )

        if len(subnets) == 0:
            self.log.emit(
                'no subnets found for role: {}'.format(role_name), 'warning'
            )
            # exit early.
            return None

        # sort by subnets by amount of instances, smallest first.
        subnets = sorted(
                      subnets,
                      key = lambda sn : collection_len(sn.instances),
                  )

        # determine the count of this role's existing instances.
        # Note: we look for role in all subnets, not just the listed subnets.
        existing_count = len(self.evpc.get_role(role_name))

        if existing_count >= desired_count:
            # for now we exit early, maybe terminate extras...
            self.log.emit(existing_count + ' ' + desired_count, 'debug')
            return None

        # determine count of additional instances needed to reach desired_count.
        needed_count      = desired_count - existing_count
        needed_per_subnet = needed_count / len(subnets)
        needed_remainder  = needed_count % len(subnets)

        role_instances = []

        for subnet in subnets:
            # ensure Run_Instance_Idempotency.html#client-tokens
            client_token = str(uuid4())

            # figure out how many instances this subnet needs to create ...
            existing_in_subnet = len(self.evpc.get_role(role_name, subnet.instances.all()))
            count = needed_per_subnet - existing_in_subnet
            if needed_remainder != 0:
                needed_remainder -= 1
                count += 1

            if count == 0:
                # skip this subnet, it doesn't need to launch any instances.
                continue

            subnet_name = make_tag_dict(subnet)['Name']
            msg = '{} instances of role {} launching into {}'
            self.log.emit(msg.format(count, role_name, subnet_name))

            # create a batch of instances in subnet!
            instances = subnet.create_instances(
                       ImageId           = ami,
                       InstanceType      = role_data.get('instance_type'),
                       MinCount          = count,
                       MaxCount          = count,
                       KeyName           = key_pair.name,
                       SecurityGroupIds  = get_ids(security_groups),
                       ClientToken       = client_token,
            )
            # accumulate all new instances into a single list.
            role_instances += instances

        # cast role Instance objets to EnrichedInstance objects.
        role_instances = self.evpc.get_instances(role_instances)

        self.tag_instances(role_name, role_instances)

        return role_instances

    def tag_instances(self, role_name, instances):
        """Accept a list of EnrichedInstance, objects create tags."""
        msg = 'tagging instance {} (Name:{}, role:{})'
        for instance in instances:
            h = '{}-{}-{}'
            hostname = h.format(self.evpc.name, role_name, instance.id_human)
            self.log.emit(msg.format(instance.identity, hostname, role_name))
            update_tags(instance, Name = hostname, role = role_name)

    def tag_instance_volumes(self, instance):
        """Accept an EnrichedInstance, tag all attached volumes."""
        msg = 'tagging volumes for instance {} (Name:{})'
        for volume in instance.volumes.all():
            self.log.emit(msg.format(instance.identity, instance.identity))
            update_tags(volume, Name = instance.identity)

    def add_eip_to_instance(self, instance):
        eip1_msg = 'allocating eip and associating with {}'
        eip2_msg = 'allocated eip {} and associated with {}'
        self.log.emit(eip1_msg.format(instance.identity))
        eip = instance.allocate_eip()
        self.log.emit(eip2_msg.format(eip.public_ip, instance.identity))

    def finish_instance_roles(self, instance_role_cfg, instances):
        for instance in instances:
            self.log.emit('waiting for {} to start'.format(instance.identity))
            instance.wait_until_running()
            self.tag_instance_volumes(instance)

            # allocate eips and associate for the needful instances.
            if instance_role_cfg[instance.role].get('eip', False) == True:
                self.add_eip_to_instance(instance)

        try:
            self.log.emit('locking new instances to prevent termination')
            self.evpc.lock_instances(instances)
        except:
            self.log.emit('could not lock instances, continuing...', 'warning')

    def db_instances(self, db_instance_cfg):
        """Build RDS DB Instances."""

        for rds_name, db_cfg in db_instance_cfg.items():

            self.log.emit('creating {} RDS db_instance ...'.format(rds_name))

            # make list of security group ids.
            security_groups = map(
                self.evpc.get_security_group,
                db_cfg.get('security_groups', [])
            )
            sg_ids = get_ids(security_groups)

            # make list of subnet ids.
            subnets = map(
                self.evpc.get_subnet,
                db_cfg.get('subnets', [])
            )
            sn_ids = get_ids(subnets)

            self.evpc.rds.create_db_subnet_group(
              DBSubnetGroupName = rds_name,
              DBSubnetGroupDescription = db_cfg.get('description',''),
              SubnetIds = sn_ids,
            )

            self.evpc.rds.create_db_instance(
              DBInstanceIdentifier = rds_name,
              DBSubnetGroupName    = rds_name,
              DBName = db_cfg.get('name', rds_name),
              VpcSecurityGroupIds   = sg_ids,
              DBInstanceClass       = db_cfg.get('class', 'db.t2.medium'),
              AllocatedStorage      = db_cfg.get('allocated_storage', 100),
              Engine                = db_cfg.get('engine'),
              EngineVersion         = db_cfg.get('engine_version', ''),
              Iops                  = db_cfg.get('iops', 0),
              MultiAZ               = db_cfg.get('multi_az', False),
              MasterUsername        = db_cfg.get('master_username'),
              MasterUserPassword    = generate_password(16),
              BackupRetentionPeriod = db_cfg.get('backup_retention_period', 0),
              Tags = [ { 'Key' : 'vpc_name', 'Value' : self.evpc.vpc_name } ],
            )

    def load_balancers(self, load_balancer_cfg):
        """Build ELB load balancers."""
        for lb_name, lb_cfg in load_balancer_cfg.items():

            lb_fullname = '{}-{}'.format(self.evpc.name, lb_name)
            self.log.emit('creating {} load_balancer ...'.format(lb_fullname))

            # make list of security group ids.
            security_groups = map(
                self.evpc.get_security_group,
                lb_cfg.get('security_groups', [])
            )
            sg_ids = get_ids(security_groups)

            # make list of subnet ids.
            subnets = map(
                self.evpc.get_subnet,
                lb_cfg.get('subnets', [])
            )
            sn_ids = get_ids(subnets)

            scheme = 'internal'
            if lb_cfg.get('internal', True) == False:
                scheme = 'internet-facing'

            listeners = self.evpc.elb.format_listeners(lb_cfg.get('listeners', []))

            self.evpc.elb.create_load_balancer(
              LoadBalancerName = lb_fullname,
              Subnets = sn_ids,
              SecurityGroups = sg_ids,
              Scheme = scheme,
              Tags = [ { 'Key' : 'vpc_name', 'Value' : self.evpc.vpc_name } ],
              Listeners = listeners,
            )

            self.log.emit('created {} load_balancer ...'.format(lb_fullname))

            self.evpc.elb.register_role_with_load_balancer(lb_fullname, lb_cfg['instance_role'])
