from unittest import TestCase

from botoform.util import (
  Log,
  dict_to_key_value,
  key_value_to_dict,
)

class TestLog(TestCase):
    """Test Suite for Log class."""
    def setUp(self):
        self.log = Log()

    def test_levels_property(self):
        """test that levels property depends on desired_level."""
        self.assertEqual(len(self.log.levels), 4)
        self.log.desired_level = 'warning'
        self.assertEqual(len(self.log.levels), 2)
        self.assertIn('warning', self.log.levels)

    def test_emit_is_false(self):
        """test that emit returns False if message level not in levels."""
        self.log.desired_level = 'warning'
        self.assertFalse(self.log.emit('taco', 'info'))

    def test_emit_is_true(self):
        """test that emit returns True if message level in levels."""
        self.assertTrue(self.log.emit('taco', 'info'))


def test_dict_to_key_value():
    data = {'key1':'value1','key2':'value2'}
    pretty_str = dict_to_key_value(data)
    assert('key1=value1' in pretty_str)
    assert('key2=value2' in pretty_str)
    assert(pretty_str.count(','), 1)
    not_as_pretty = dict_to_key_value(data,'x','x')
    assert(not_as_pretty.count('x'), 3)

def test_key_value_to_dict():
    key_value_list = ['a=1,b=2', 'c=3, d=4', 'e=5']
    desired_result = {'a':'1', 'b':'2', 'c':'3', 'd':'4', 'e':'5'}
    assert(key_value_to_dict(key_value_list) == desired_result)

