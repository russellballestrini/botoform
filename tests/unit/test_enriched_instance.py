from unittest import TestCase

from mock import Mock

from botoform.evpc import EnrichedInstance

class MockInstanceSpec(object):
    """Mock Boto3's ec2.Instance class."""
    id   = 'i-mock1234'
    tags = [{u'Value': 'vpc-mock1234', u'Key': 'vpc-id'},
            {u'Value': 'webapp01-web01', u'Key': 'Name'}]

class TestEnrichedInstance(TestCase):

    def setUp(self):
        MockInstance = Mock(name="Instance", return_value = MockInstanceSpec())
        self.einstance1 = EnrichedInstance(MockInstance())
        self.einstance2 = EnrichedInstance(MockInstance())

    def test_equal(self):
        self.assertEqual(self.einstance1, self.einstance2)

    def test_not_equal(self):
        self.einstance2.id = 'i-mock4321'
        self.assertNotEqual(self.einstance1, self.einstance2)

    def test_hostname(self):
        self.assertEqual('webapp01-web01', self.einstance1.hostname)

    def test_shortname(self):
        self.assertEqual('web01', self.einstance1.shortname)

    def test_role(self):
        self.assertEqual('web', self.einstance1.role)
