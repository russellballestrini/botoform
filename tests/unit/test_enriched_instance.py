from unittest import TestCase

from mock import Mock

from botoform.evpc import EnrichedInstance

class MockInstanceSpec(object):
    """Mock Boto3's ec2.Instance class."""
    tags = [{u'Value': 'vpc-mock1234', u'Key': 'vpc-id'},
            {u'Value': 'webapp01-web01', u'Key': 'Name'}]

class TestEnrichedInstance(TestCase):

    def setUp(self):
        MockInstance = Mock(name="Instance", return_value = MockInstanceSpec())
        self.einstance = EnrichedInstance(MockInstance())

    def test_hostname(self):
        self.assertEqual('webapp01-web01', self.einstance.hostname)

    def test_shortname(self):
        self.assertEqual('web01', self.einstance.shortname)

    def test_role(self):
        self.assertEqual('web', self.einstance.role)
