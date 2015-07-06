from helpers import BotoformTestCase

class TestEnrichedInstance(BotoformTestCase):

    def test_equal(self):
        self.assertEqual(self.einstance1, self.einstance3)

    def test_not_equal(self):
        self.assertNotEqual(self.einstance1, self.einstance2)

    def test_hostname(self):
        self.assertEqual('webapp01-web01', self.einstance1.hostname)

    def test_shortname(self):
        self.assertEqual('web01', self.einstance1.shortname)

    def test_role(self):
        self.assertEqual('web', self.einstance1.role)


