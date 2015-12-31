from helpers import BotoformTestCase

from mock import MagicMock

class TestEnrichedInstance(BotoformTestCase):

    def test_equal(self):
        self.assertEqual(self.instance1, self.instance1b)

    def test_not_equal(self):
        self.assertNotEqual(self.instance1, self.instance2)

    def test_hostname(self):
        self.assertEqual('webapp01-web01', self.instance1.hostname)

    def test_shortname(self):
        self.assertEqual('web01', self.instance1.shortname)

    def test_role_from_role_tag(self):
        self.assertEqual('vpn', self.instance4.role)

    def test_role_from_name_tag(self):
        self.assertEqual('web', self.instance1.role)

    def test_id(self):
        self.assertEqual('i-mock1111', self.instance1.id)

    def test_identity_and_str(self):
        """The identity property of EnrichedInstance returns hostname or id."""
        self.assertEqual('webapp01-web01', self.instance1.identity)
        self.assertEqual('webapp01-web01', self.instance1.__str__())
        # remove Name tag to cause hostname to be None.
        self.instance1.instance.tags = []
        self.assertEqual('i-mock1111', self.instance1.identity)
        self.assertEqual('i-mock1111', self.instance1.__str__())

    def test_identifiers(self):
        self.assertEqual(len(self.instance1.identifiers), 4)
        self.assertEqual(len(self.instance2.identifiers), 4)
        # instance3 has a public_ip_address identifier.
        self.assertEqual(len(self.instance3.identifiers), 5)


