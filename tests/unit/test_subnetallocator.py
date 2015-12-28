from unittest import TestCase

from botoform.subnetallocator import allocate

class TestSubnetAllocator(TestCase):

    def test_allocate_returns_desired_network_list(self):
        desired_allocations = ['10.0.6.0/26', '10.0.6.64/29', '10.0.6.72/29']
        allocations = map(str, allocate('10.0.6.0/24', [26,29,29]))
        self.assertListEqual(allocations, desired_allocations)
        self.assertEqual(len(allocations), 3)

    def test_allocate_sizes_sorted(self):
        desired_allocations = ['10.0.6.0/26', '10.0.6.64/29', '10.0.6.72/29']
        allocations = map(str, allocate('10.0.6.0/24', [29,26,29]))
        self.assertListEqual(allocations, desired_allocations)
        self.assertEqual(len(allocations), 3)

    def test_allocate_many_subnets(self):
        desired_allocations = ['10.0.6.0/26', '10.0.6.64/26',
                               '10.0.6.128/26', '10.0.6.192/27',
                               '10.0.6.224/28', '10.0.6.240/28']
        allocations = map(str, allocate('10.0.6.0/24', [26,26,26,27,28,28]))
        self.assertEqual(len(allocations), 6)
        self.assertListEqual(allocations, desired_allocations)

    def test_allocate_many_subnets_2(self):
        desired_allocations = ['10.0.6.0/26', '10.0.6.64/26', '10.0.6.128/27',
                               '10.0.6.160/27', '10.0.6.192/27', '10.0.6.224/28']
        allocations = map(str, allocate('10.0.6.0/24', [26,26,27,27,27,28]))
        self.assertEqual(len(allocations), 6)
        self.assertListEqual(allocations, desired_allocations)

    def test_allocate_too_many_subnets_exception(self):
        with self.assertRaises(Exception):
            allocate('10.0.6.0/24', [26,26,26,27,28,28,29])

    def test_allocate_too_many_subnets_exception_2(self):
        with self.assertRaises(Exception):
            allocate('10.0.6.0/24', [26,26,26,27,28,28,28])


