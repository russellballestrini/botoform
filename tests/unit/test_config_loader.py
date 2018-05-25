from unittest import TestCase

from botoform.config import ConfigLoader

TEMPLATE_PATH = "tests/fixtures/webapp.yaml"


class TestConfigLoader(TestCase):

    def setUp(self):
        self.template_path = TEMPLATE_PATH
        with open(TEMPLATE_PATH) as f:
            self.template_string = f.read()
        self.context_vars = {"vpc_name": "webapp01", "vpc_cidr": "192.168.1.1/24"}

    def test_constructor_default_context_vars_is_empty_dict(self):
        loader = ConfigLoader()
        self.assertTrue(len(loader.context_vars) == 0)
        self.assertEqual(loader.context_vars, {})

    def test_constructor_context_vars_is_set(self):
        loader = ConfigLoader(context_vars=self.context_vars)
        self.assertTrue(len(loader.context_vars.keys()) == 2)
        self.assertTrue("vpc_cidr" in loader.context_vars.keys())

    def test_load_template_file_without_context(self):
        loader = ConfigLoader()
        config = loader.load(template_path=self.template_path)
        self.assertEqual(len(config), 12)
        self.assertEqual(len(config["instance_roles"]), 4)
        self.assertEqual(len(config["amis"]), 4)
        self.assertEqual(len(config["security_groups"]), 7)
        self.assertEqual(len(config["security_groups"]["web"]["inbound"]), 1)

    def test_load_template_string_without_context(self):
        loader = ConfigLoader()
        loader.template_dir = "tests/fixtures"
        config = loader.load(template_string=self.template_string)
        self.assertEqual(len(config), 12)
        self.assertEqual(len(config["instance_roles"]), 4)
        self.assertEqual(len(config["amis"]), 4)
        self.assertEqual(len(config["security_groups"]), 7)
        self.assertEqual(len(config["security_groups"]["web"]["inbound"]), 1)

    def test_load_template_with_boolean(self):
        loader = ConfigLoader()
        config = loader.load(template_path=self.template_path)
        self.assertEqual(config["instance_roles"]["web"]["autoscaling"], True)
