from unittest import TestCase

from mock import Mock

from botoform.evpc import EnrichedVPC
from botoform.evpc import EnrichedInstance

class MockVPCSpec1(object):
    """Mock Boto3's ec2.Vpc class."""
    id   = 'vpc-mock1111'
    tags = [{u'Value': 'webapp01', u'Key': 'Name'}]


class MockInstanceSpec1(object):
    """Mock Boto3's ec2.Instance class."""
    id   = 'i-mock1111'
    tags = [{u'Value': 'vpc-mock1111', u'Key': 'vpc-id'},
            {u'Value': 'webapp01-web01', u'Key': 'Name'}]


class MockInstanceSpec2(object):
    """Mock Boto3's ec2.Instance class."""
    id   = 'i-mock2222'
    tags = [{u'Value': 'vpc-mock1111', u'Key': 'vpc-id'},
            {u'Value': 'webapp01-web02', u'Key': 'Name'}]


class BotoformTestCase(TestCase):

    def setUp(self):
        MockInstance = Mock(name="Instance", return_value = MockInstanceSpec1())
        self.einstance1 = EnrichedInstance(MockInstance())
        self.einstance3 = EnrichedInstance(MockInstance())

        MockInstance = Mock(name="Instance", return_value = MockInstanceSpec2())
        self.einstance2 = EnrichedInstance(MockInstance())

        MockVPC = Mock(name="VPC", return_value = MockVPCSpec1())
        #self.evpc1 = MockVPC()
        self.evpc1 = EnrichedVPC()


