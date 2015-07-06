from helpers import BotoformTestCase

class TestEnrichedInstance(BotoformTestCase):

    def test_equal(self):
        self.assertEqual(self.instance1, self.instance3)

    def test_not_equal(self):
        self.assertNotEqual(self.instance1, self.instance2)

    def test_hostname(self):
        self.assertEqual('webapp01-web01', self.instance1.hostname)

    def test_shortname(self):
        self.assertEqual('web01', self.instance1.shortname)

    def test_role(self):
        self.assertEqual('web', self.instance1.role)


