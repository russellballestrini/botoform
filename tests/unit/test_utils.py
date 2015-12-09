from unittest import TestCase

from botoform.util import (
  Log,
  dict_to_key_value,
  key_value_to_dict,
  snake_to_camel_case,
  make_tag_dict,
  get_port_range,
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


class TestSnakeToCamelCase(TestCase):
    """Test Suite for snake_to_camel_case function."""
    def setUp(self):
        self.answers = {'http_response':'HTTPResponse'}

    def test_name_cidr_block(self):
        self.assertEqual(
          snake_to_camel_case('cidr_block'),
          'CidrBlock'
        )

    def test_name_http_response(self):
        # this tests short circut of answers.
        self.assertEqual(
          snake_to_camel_case('http_response', answers=self.answers),
          'HTTPResponse'
        )

    def test_name_vpc_id(self):
        self.assertEqual(
          snake_to_camel_case('vpc_id'),
          'VpcId'
        )


class TestGetPortRange(TestCase):

    def test_all_port(self):
        self.assertTupleEqual(get_port_range('all'), (1, 65535))

    def test_all_caps_port(self):
        self.assertTupleEqual(get_port_range('ALL'), (1, 65535))

    def test_icmp_is_negative_one_tuple(self):
        self.assertTupleEqual(get_port_range('anything', 'icmp'), (-1, -1))

    def test_all_mixed_port_raises_value_error(self):
        with self.assertRaises(ValueError):
            get_port_range('aLL')

    def test_taco_port_raises_value_error(self):
        with self.assertRaises(ValueError):
            get_port_range('taco')

    def test_no_port_raises_exception(self):
        with self.assertRaises(TypeError):
            get_port_range()

    def test_empty_port_raises_exception(self):
        with self.assertRaises(Exception):
            get_port_range('')

    def test_443_port(self):
        self.assertTupleEqual(get_port_range('443'), (443, 443))

    def test_5000_5009_port(self):
        self.assertTupleEqual(get_port_range('5000-5009'), (5000, 5009))

    def test_5000_5009_port_with_whitespace(self):
        self.assertTupleEqual(get_port_range(' 5000-  5009'), (5000, 5009))


def test_make_tag_dict():
    class TestSubject(object):
        tags = [
          {'Key':'Name', 'Value':'myapp01-web01'},
          {'Key':'role', 'Value':'web'},
        ]
    obj = TestSubject
    tags = make_tag_dict(obj)
    assert('Name' in tags)
    assert('role' in tags)
    assert(tags['Name'] == 'myapp01-web01')
    assert(tags['role'] == 'web')

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

