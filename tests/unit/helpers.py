from unittest import TestCase

from mock import (
  mock,
  Mock,
  MagicMock,
)

from botoform.enriched import EnrichedVPC
from botoform.enriched import EnrichedInstance

class MockInstanceSpec1(object):
    """Mock Boto3's ec2.Instance class."""
    id   = 'i-mock1111'
    tags = [{u'Value': 'vpc-mock1111', u'Key': 'vpc-id'},
            {u'Value': 'webapp01-web01', u'Key': 'Name'}]
    public_ip_address = None
    private_ip_address = '192.168.1.31'


class MockInstanceSpec2(object):
    """Mock Boto3's ec2.Instance class."""
    id   = 'i-mock2222'
    tags = [{u'Value': 'vpc-mock1111', u'Key': 'vpc-id'},
            {u'Value': 'webapp01-web02', u'Key': 'Name'}]
    public_ip_address = None
    private_ip_address = '192.168.1.32'


class MockInstanceSpec3(object):
    """Mock Boto3's ec2.Instance class."""
    id   = 'i-mock3333'
    tags = [{u'Value': 'vpc-mock1111', u'Key': 'vpc-id'},
            {u'Value': 'webapp01-proxy01', u'Key': 'Name'}]
    public_ip_address = '54.1.1.3'
    private_ip_address = '192.168.1.33'


class BotoformTestCase(TestCase):

    @mock.patch('botoform.enriched.EnrichedVPC.attach_boto_clients',
                mock.Mock(return_value=None))
    def setUp(self):
        MockInstance1 = Mock(name="Instance", return_value = MockInstanceSpec1())
        self.instance1 = EnrichedInstance(MockInstance1())
        self.instance1b = EnrichedInstance(MockInstance1())

        MockInstance2 = Mock(name="Instance", return_value = MockInstanceSpec2())
        self.instance2 = EnrichedInstance(MockInstance2())

        MockInstance3 = Mock(name="Instance", return_value = MockInstanceSpec3())
        self.instance3 = EnrichedInstance(MockInstance3())

        self.evpc1 = EnrichedVPC()
        self.evpc1._ec2_instances = MagicMock(
                                      return_value=[
                                        MockInstance1(),
                                        MockInstance2(),
                                        MockInstance3(),
                                      ]
                                    )


