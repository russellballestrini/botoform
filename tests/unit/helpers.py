from unittest import TestCase

import mock

from botoform.enriched import EnrichedVPC
from botoform.enriched import EnrichedInstance

class MockInstanceSpec1(object):
    """Mock Boto3's ec2.Instance class."""
    id   = 'i-mock1111'
    tags = [{u'Value': 'vpc-mock1111', u'Key': 'vpc-id'},
            {u'Value': 'webapp01-web01', u'Key': 'Name'}]
    public_ip_address = None
    private_ip_address = '192.168.1.31'
    spot_instance_request_id = None


class MockInstanceSpec2(object):
    """Mock Boto3's ec2.Instance class."""
    id   = 'i-mock2222'
    tags = [{u'Value': 'vpc-mock1111', u'Key': 'vpc-id'},
    #        {u'Value': 'webapp01-web02', u'Key': 'Name'}]
            {u'Value': 'webapp01-web-02', u'Key': 'Name'}]
    public_ip_address = None
    private_ip_address = '192.168.1.32'
    spot_instance_request_id = None


class MockInstanceSpec3(object):
    """Mock Boto3's ec2.Instance class."""
    id   = 'i-mock3333'
    tags = [{u'Value': 'vpc-mock1111', u'Key': 'vpc-id'},
            {u'Value': 'webapp01-proxy01', u'Key': 'Name'}]
    public_ip_address = '54.1.1.3'
    private_ip_address = '192.168.1.33'
    spot_instance_request_id = None

class MockInstanceSpec4(object):
    """Mock Boto3's ec2.Instance class."""
    id   = 'i-mock4444'
    tags = [
             {u'Value': 'vpc-mock1111', u'Key': 'vpc-id'},
             {u'Value': 'webapp01-test', u'Key': 'Name'},
             {u'Value': 'vpn', u'Key': 'role'},
           ]
    public_ip_address = '54.1.1.4'
    private_ip_address = '192.168.1.44'
    spot_instance_request_id = 'sir-xxxxxxx4'

class BotoformTestCase(TestCase):

    @mock.patch('botoform.util.BotoConnections.refresh_boto_connections',
                mock.Mock(return_value=None))
    def setUp(self):
        MockInstance1 = mock.Mock(name="Instance", return_value = MockInstanceSpec1())
        self.instance1 = EnrichedInstance(MockInstance1())
        self.instance1b = EnrichedInstance(MockInstance1())

        MockInstance2 = mock.Mock(name="Instance", return_value = MockInstanceSpec2())
        self.instance2 = EnrichedInstance(MockInstance2())

        MockInstance3 = mock.Mock(name="Instance", return_value = MockInstanceSpec3())
        self.instance3 = EnrichedInstance(MockInstance3())

        MockInstance4 = mock.Mock(name="Instance", return_value = MockInstanceSpec4())
        self.instance4 = EnrichedInstance(MockInstance4())

        self.evpc1 = EnrichedVPC()
        self.evpc1._ec2_instances = mock.MagicMock(
                                      return_value=[
                                        MockInstance1(),
                                        MockInstance2(),
                                        MockInstance3(),
                                        MockInstance4(),
                                      ]
                                    )


