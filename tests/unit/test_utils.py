from botoform.util import (
  dict_to_key_value,
  key_value_to_dict,
)

def test_dict_to_key_value():
    data = {'key1':'value1','key2':'value2'}
    pretty_str = dict_to_key_value(data)
    assert('key1=value1' in pretty_str)
    assert('key2=value2' in pretty_str)
    assert('key1=value1,key2=value2' in pretty_str)
    not_as_pretty = dict_to_key_value(data,'x','x')
    assert('key1xvalue1xkey2xvalue2' in not_as_pretty)

def test_key_value_to_dict():
    key_value_list = ['a=1,b=2', 'c=3, d=4', 'e=5']
    desired_result = {'a':'1', 'b':'2', 'c':'3', 'd':'4', 'e':'5'}
    assert(key_value_to_dict(key_value_list) == desired_result)

