from unittest import TestCase

from mock import (
  Mock,
  MagicMock,
)

from botoform.evpc import EnrichedVPC
from botoform.evpc import EnrichedInstance

class MockInstanceSpec1(object):
    """Mock Boto3's ec2.Instance class."""
    id   = 'i-mock1111'
    tags = [{u'Value': 'vpc-mock1111', u'Key': 'vpc-id'},
            {u'Value': 'webapp01-web01', u'Key': 'Name'}]


class MockInstanceSpec2(object):
    """Mock Boto3's ec2.Instance class."""
    id   = 'i-mock2222'
    tags = [{u'Value': 'vpc-mock1111', u'Key': 'vpc-id'},
            {u'Value': 'webapp01-proxy02', u'Key': 'Name'}]


class BotoformTestCase(TestCase):

    def setUp(self):
        MockInstance1 = Mock(name="Instance", return_value = MockInstanceSpec1())
        self.instance1 = EnrichedInstance(MockInstance1())
        self.instance3 = EnrichedInstance(MockInstance1())

        MockInstance2 = Mock(name="Instance", return_value = MockInstanceSpec2())
        self.instance2 = EnrichedInstance(MockInstance2())

        self.evpc1 = EnrichedVPC()
        self.evpc1._ec2_instances = MagicMock(return_value=[MockInstance1(), MockInstance2()])


