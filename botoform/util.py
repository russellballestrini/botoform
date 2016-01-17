import yaml
import json
import boto3

import hashlib
import humanhash

class BotoConnections(object):
    """Central Management of boto3 client and resource connection objects."""
    def __init__(self, region_name=None, profile_name=None):
        """
        Optionally pass region_name and profile_name. Setup boto3 session.
        Attach boto3 client and resource connection objects.
        """
        # defaults.
        self._region_name = self._profile_name = None
        # trigger region_name.setter
        self.region_name = region_name
        # trigger profile_name.setter
        self.profile_name = profile_name

    @property
    def profile_name(self):
        return self._profile_name

    @profile_name.setter
    def profile_name(self, new_name):
        """set profile_name and refresh_boto_connections"""
        self._profile_name = new_name
        self.setup_session_and_refresh_connections()

    @property
    def region_name(self):
        return self._region_name

    @region_name.setter
    def region_name(self, new_name):
        """set region_name and refresh_boto_connections"""
        self._region_name = new_name
        self.setup_session_and_refresh_connections()

    def setup_session_and_refresh_connections(self):
        if self.profile_name and self.region_name:
            boto3.setup_default_session(
              profile_name = self.profile_name,
              region_name  = self.region_name,
            )
        elif self.profile_name:
            boto3.setup_default_session(profile_name = self.profile_name)
        elif self.region_name:
            boto3.setup_default_session(region_name = self.region_name)
        else:
            return None
        self.refresh_boto_connections()

    def refresh_boto_connections(self):
        """Attach related Boto3 clients and resources."""
        self.ec2 = boto3.resource('ec2')
        self.ec2_client = boto3.client('ec2')
        self.rds = boto3.client('rds')
        self.elasticache = boto3.client('elasticache')
        self.elb = boto3.client('elb')

    @property
    def azones(self):
        """Return a list of available AZ names for active AWS profile/region."""
        az_filter = make_filter('state', 'available')
        azs = self.ec2_client.describe_availability_zones(Filters=az_filter)
        return map(lambda az : az['ZoneName'], azs['AvailabilityZones'])


class BotoformDumper(yaml.Dumper):
    """A custom YAML dumper that is pretty."""
    def increase_indent(self, flow=False, indentless=False):
        return super(BotoformDumper, self).increase_indent(flow, False)


class Log(object):
    """Handles emitting logs to syslog and stdout."""
    def __init__(self, desired_level='debug', syslog=True, stdout=True, program='botoform'):
        """
        Setup Log object with desired parameters

        :param desired_level:
          The lowest severity level to log (default debug).

        :param stdout:
          Boolean to determine if messages should emit to STDOUT (default True).

        :param stdout:
          Boolean to determine if messages should emit to syslog (default True).

        :param program:
          The program field used by syslog (default botoform).
        """
        # order matters.
        self.all_levels  = ['debug', 'info', 'warning', 'error']
        self.desired_level = desired_level
        self.stdout  = stdout
        self.syslog  = syslog
        self.program = program

    @property
    def levels(self):
        """Return a list of levels on and beyond desired_level."""
        return self.all_levels[self.all_levels.index(self.desired_level):]

    def emit(self, message, level='info'):
        """
        Emit message if level meets requirement.

        message:
          Any object that has a __str__ method.

        level:
          The level or severity of this message (default info)
        """
        if level not in self.levels:
            return False

        if self.stdout == True:
            print(message)

        if self.syslog == True:
            # TODO: some sysloggy stuff here.
            pass

        return True


def output_formatter(data, output_format='newline'):
    """Print data in the optional output_format."""
    if output_format.lower() == 'newline':
        output = '\n'.join(data)
    elif output_format.upper() == 'CSV':
        output = ', '.join(data)
    elif output_format.upper() == 'YAML':
        output = yaml.dump(data, Dumper=BotoformDumper)
    elif output_format.upper() == 'JSON':
        output = json.dumps(data, indent=2)
    return output

def reflect_attrs(child, parent, skip_attrs=None):
    """
    Composition Magic: reflect all missing parents attributes into child.

    :param child: Object to receive attributes.
    :param parent: Object to source attributes from.
    :param skip_attrs: Optional list of attrs strings to not reflect.

    :returns: None
    """
    skip_attrs = skip_attrs if skip_attrs is not None else []
    for attr in dir(parent):
        if attr not in skip_attrs:
            child.__dict__[attr] = getattr(parent, attr)

def merge_pages(key, pages):
    """
    Merge boto3 paginated results into single list.

    :param key: The document key to merge from all pages.
    :param pages: An iterator of page documents.

    :returns: A single flat list containing results of all pages.
    """
    results = []
    for page in pages:
        results += page[key]
    return results

def get_ids(objects):
    """
    Return a list of ids from a list of objects.

    :param objects: A list of objects all of whom have an id attribute.

    :returns: A list of ids
    """
    return [o.id for o in objects if o is not None]

def collection_len(collection):
    return len(list(collection.all()))

def make_filter(key, values):
    """
    Return a filter document expected by Boto3.

    :param key: The key name for this new filter document.
    :param values: A value or a list of values to filter/match on.

    :returns: A filter document (list/dict) in the form that Boto3 expects.
    """
    values = values if isinstance(values, list) else [values]
    return [ { 'Name' : key, 'Values' : values } ]


def tag_filter(tag_key, tag_values):
    """
    Return a tag filter document expected by boto3.

    :param tag_key: A tag key or name.
    :param tag_values: The tag value or a list of values to filter on.

    :returns: A filter document (list/dict) in the form that Boto3 expects.
    """
    return make_filter('tag:{}'.format(tag_key), tag_values)

def make_tag_dict(ec2_object):
    """
    Return a dictionary of existing tags.

    :param ec2_object: A tagable Boto3 object with a tags attribute.

    :returns: A dictionary where tag names are keys and tag values are values.
    """
    tag_dict = {}
    if ec2_object.tags is None: return tag_dict
    for tag in ec2_object.tags:
        tag_dict[tag['Key']] = tag['Value']
    return tag_dict

def update_tags(ec2_object, **kwargs):
    """
    Add or update tags to reflect given keyword args

    :param ec2_object: A tagable Boto3 object with a tags attribute.
    :param \*\*kwargs: key=value where key is tag name, value is tag value.

    :returns: None
    """
    tags_to_update = []
    tag_dict = make_tag_dict(ec2_object)
    for key, value in kwargs.iteritems():
        if tag_dict.get(key, None) != value:
            tags_to_update.append({'Key' : key, 'Value' : value})
    ec2_object.create_tags(Tags = tags_to_update)

def dict_to_key_value(data, sep='=', pair_sep=','):
    """
    Return a string representation of a dictionary.

    by default this function will turn::

      {'key1':'value1','key2':'value2'}

    into::

      key1=value1,key2=value2

    :param data: The dictionary to convert into a string.
    :param sep: Optional, string to separate keys and values (Default '=')
    :param pair_sep: Optional, string to separate key/value pairs (Default ',')

    :returns: a string representation of the given dictionary.
    """
    return pair_sep.join([sep.join(key_value) for key_value in data.items()])

def key_value_to_dict(key_value_list, sep='=', pair_sep=','):
    """
    Return a dictionary from a list of key/value strings.

    turns key_value_list, like::

      key_value_list = ['a=1,b=2', 'c=3, d=4', 'e=5']

    into a dict, like::

      {'a':'1', 'b':'2', 'c':'3', 'd':'4', 'e':'5'}

    :param key_value_list:
      The list of key/value strings to convert into a dict.
    :param sep:
      Optional, string which separates keys and values (Default '=')
    :param pair_sep:
      Optional, string which separates key/value pairs (Default ',')

    :returns: A string representation of the given dictionary.
    """
    d = {}
    # allow user to pass a string or a list of strings.
    if isinstance(key_value_list, str): key_value_list = [key_value_list]
    for speclist in key_value_list:
        for spec in speclist.strip().split(','):
            key, value = spec.strip().split('=')
            d[key] = value
    return d

def get_port_range(raw_range, ip_protocol='tcp'):
    """
    Returns a (from_port, to_port) tuple.

    Examples:

    .. code-block:: python

      >>> get_port_range(443)
      (443, 443)

      >>> get_port_range('all')
      (1, 65535)

      >>> get_port_range('5000-5009')
      (5000, 5009)

      >>> get_port_range(' 8080')
      (8080, 8080)

      >>> get_port_range('tacobell', ip_protocol='icmp')
      (-1, -1)

    :param raw_range: A string or integer.

    :param ip_protocol: Optional, 'tcp', 'udp', 'icpm' (Default 'tcp')

    :returns: (from_port, to_port)
    """
    if not raw_range:
        raise Exception('Missing or empty port range')

    if ip_protocol == 'icmp':
        return (-1, -1)

    raw_range = str(raw_range).replace(' ','')

    if raw_range == 'all' or raw_range == 'ALL':
        port_range = [1, 65535]
    elif '-' in raw_range:
        port_range = raw_range.split('-')
    else:
        port_range = [raw_range, raw_range]
    return tuple(map(int, port_range))

def write_private_key(key_pair):
    """
    Write private key to filesystem.

    :param key_pair: The Boto3 KeyPair object to write to filesystem.

    :returns None:
    """
    from os import chmod
    private_key_path = key_pair['KeyName'] + '.pem'
    with open(private_key_path, 'w') as f:
        f.write(key_pair['KeyMaterial'])
        chmod(private_key_path, 0400)

def id_to_human(id_string):
    """
    Turn an id into a human readable hash digest.

    :param id_string:
        The subject string to generate a human hash of.

    >>> id_to_human('i-ceebb70c')
    'friendisland'
    """
    id_sha512 = hashlib.sha512(id_string).hexdigest()
    return humanhash.humanize(id_sha512, 2, '')

def snake_to_camel_case(name, answers=None):
    """
    Accept a snake_case string and return a CamelCase string.

    For example::

      >>> snake_to_camel_case('cidr_block')
      'CidrBlock'
    """
    if answers is not None:
        if name in answers:
            return answers[name]
    return ''.join(word.capitalize() for word in name.split('_'))

