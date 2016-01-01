from time import strftime

from botoform.util import (
  update_tags,
  write_private_key,
)

class EnrichedKeyPair(object):

    def __init__(self, evpc):
        # save the EnrichedVpc object.
        self.evpc = evpc

    @property
    def key_names(self):
        """Return a list of ssh key pair names from AWS VPC tag."""
        key_name_csv = self.evpc.tag_dict.get('key_pairs', None)
        key_names = []
        if key_name_csv is not None:
            key_names = key_name_csv.split(',')
        return key_names

    @property
    def key_pairs(self):
        """Return a dictionary of ssh KeyPair objects."""
        key_pairs = {}
        for key_name in self.key_names:
            key_pairs[key_name] = self.evpc.boto.ec2.KeyPair(key_name)
        return key_pairs

    def get_key_name(self, short_key_pair_name):
        """Returns full key_name if key exists, else None"""
        name = '{}-{}'.format(self.evpc.name, short_key_pair_name)
        for key_name in self.key_names:
            if key_name.startswith(name):
                return key_name

    def get_key_pair(self, short_key_pair_name):
        """Return a KeyPair object by key_name."""
        key_name = self.get_key_name(short_key_pair_name)
        if key_name is not None:
            return self.evpc.boto.ec2.KeyPair(key_name)
            
    def _update_key_pairs_tag(self, key_names):
        update_tags(self.evpc, key_pairs = ','.join(key_names))

    def create_key_pair(self, short_key_pair_name):
        """Create a KeyPair object, update key_pairs AWS tag."""
        key_pair = self.get_key_pair(short_key_pair_name)
        if key_pair is not None:
            # exit early, key_pair already exists.
            return None

        date_time = strftime("%Y%m%d-%H%M")
        key_pair_name = '{}-{}-{}'.format(
                            self.evpc.name,
                            short_key_pair_name,
                            date_time,
                        )

        key_pair = self.evpc.boto.ec2_client.create_key_pair(KeyName=key_pair_name)
        write_private_key(key_pair)

        # update evpc key_pairs aws tag.
        key_names = self.key_names
        key_names.append(key_pair_name)
        self._update_key_pairs_tag(key_names)

    def delete_key_pair(self, short_key_pair_name):
        """Delete a KeyPair object, update key_pairs AWS tag."""
        key_pair = self.get_key_pair(short_key_pair_name)
        if key_pair is None:
            # exit early, key_pair does not exists.
            return None

        # update evpc key_pairs aws tag.
        key_names = self.key_names
        key_names.remove(key_pair.name)
        self._update_key_pairs_tag(key_names)

        key_pair.delete()

    def delete_key_pairs(self):
        """Delete ALL related KeyPair objects, update key_pairs AWS tag."""
        for key_pair in self.key_pairs.values():
            key_pair.delete()
        self._update_key_pairs_tag([])


